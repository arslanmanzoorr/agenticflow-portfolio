"""PriceRadar Processor API -- FastAPI application.

Provides endpoints for competitor price monitoring, analysis, alert management,
and webhook ingestion from Apify scraper runs.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .models.price import (
    CompetitorProduct,
    DailyReport,
    PriceAlert,
    PriceComparisonRequest,
    PriceComparisonResult,
    PriceHistory,
    PriceRecord,
    PriceWebhookPayload,
)
from .services.airtable_sync import AirtableSync
from .services.price_analyzer import PriceAnalyzer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared service instances
# ---------------------------------------------------------------------------

_airtable: AirtableSync | None = None
_analyzer: PriceAnalyzer | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Initialise and tear down shared service singletons."""
    global _airtable, _analyzer  # noqa: PLW0603

    _airtable = AirtableSync()
    _analyzer = PriceAnalyzer(_airtable)

    logger.info("PriceRadar processor started")
    yield
    logger.info("PriceRadar processor shutting down")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Competitor price monitoring and analysis API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------


def _get_airtable() -> AirtableSync:
    if _airtable is None:
        raise HTTPException(status_code=503, detail="Service not initialised")
    return _airtable


def _get_analyzer() -> PriceAnalyzer:
    if _analyzer is None:
        raise HTTPException(status_code=503, detail="Service not initialised")
    return _analyzer


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Return service health status."""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# ---------------------------------------------------------------------------
# POST /analyze -- trigger price analysis
# ---------------------------------------------------------------------------


@app.post("/analyze", tags=["analysis"])
async def analyze_prices() -> dict[str, Any]:
    """Trigger a full price analysis across all tracked products.

    Detects price drops, stock changes, and generates a daily report.
    Returns a summary of findings.
    """
    analyzer = _get_analyzer()
    airtable = _get_airtable()

    try:
        report: DailyReport = analyzer.generate_daily_report()

        return {
            "status": "completed",
            "total_products_monitored": report.total_products_monitored,
            "total_competitors": report.total_competitors,
            "price_drops": len(report.price_drops),
            "price_increases": len(report.price_increases),
            "new_lowest_prices": len(report.new_lowest_prices),
            "stock_changes": len(report.stock_changes),
            "summary": report.summary,
        }

    except Exception as exc:
        logger.exception("Price analysis failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# GET /products -- list tracked products
# ---------------------------------------------------------------------------


@app.get("/products", tags=["products"])
async def list_products(
    competitor: str | None = Query(default=None, description="Filter by competitor name"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum results"),
) -> dict[str, Any]:
    """List all tracked products from Airtable.

    Optionally filter by competitor name.
    """
    airtable = _get_airtable()

    try:
        products = airtable.get_all_products()

        if competitor:
            products = [
                p for p in products
                if p.get("Competitor", "").lower() == competitor.lower()
            ]

        return {
            "total": len(products[:limit]),
            "products": products[:limit],
        }

    except Exception as exc:
        logger.exception("Failed to list products")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# GET /products/{product_id}/history -- price history for a product
# ---------------------------------------------------------------------------


@app.get("/products/{product_id}/history", tags=["products"])
async def get_product_history(product_id: str) -> dict[str, Any]:
    """Get full price history and statistics for a specific product."""
    analyzer = _get_analyzer()

    try:
        history: PriceHistory | None = analyzer.get_price_history(product_id)

        if history is None:
            raise HTTPException(
                status_code=404,
                detail=f"Product '{product_id}' not found",
            )

        trend = analyzer.calculate_trend(
            [r["price"] for r in history.records if r.get("price") is not None]
        )

        return {
            "product_id": history.product_id,
            "product_name": history.product_name,
            "competitor_name": history.competitor_name,
            "url": history.url,
            "current_price": history.current_price,
            "lowest_price": history.lowest_price,
            "highest_price": history.highest_price,
            "average_price": history.average_price,
            "price_change_30d": history.price_change_30d,
            "trend": trend,
            "total_observations": history.total_observations,
            "records": history.records,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get product history")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# GET /alerts -- recent price alerts
# ---------------------------------------------------------------------------


@app.get("/alerts", tags=["alerts"])
async def get_alerts(
    limit: int = Query(default=50, ge=1, le=200, description="Maximum alerts to return"),
) -> dict[str, Any]:
    """Get recent unacknowledged price alerts."""
    airtable = _get_airtable()

    try:
        alerts = airtable.get_active_alerts(limit=limit)

        return {
            "total": len(alerts),
            "alerts": alerts,
        }

    except Exception as exc:
        logger.exception("Failed to get alerts")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# POST /webhook/apify -- receive Apify scrape results
# ---------------------------------------------------------------------------


@app.post("/webhook/apify", tags=["webhooks"])
async def receive_apify_webhook(payload: PriceWebhookPayload) -> dict[str, Any]:
    """Receive scraped price data from an Apify actor run.

    Processes the incoming records by:
    1. Syncing product and price history to Airtable
    2. Detecting significant price drops
    3. Detecting stock availability changes
    4. Saving triggered alerts to Airtable
    """
    airtable = _get_airtable()
    analyzer = _get_analyzer()

    try:
        # 1. Sync raw records to Airtable
        sync_stats = airtable.sync_price_records(payload.products)

        # 2. Detect price drops
        drops = analyzer.detect_price_drops(
            payload.products,
            min_drop_percent=settings.PRICE_CHANGE_THRESHOLD,
        )

        # 3. Detect stock changes
        stock_changes = analyzer.detect_stock_changes(payload.products)

        # 4. Save alerts
        alerts_saved = 0
        for drop in drops:
            alert_data = {
                "alert_id": f"drop-{drop['product_id']}-{payload.scraped_at.isoformat()}",
                "alert_type": "price_drop",
                "severity": "critical" if drop["drop_percent"] > 15 else "warning",
                "product_id": drop["product_id"],
                "product_name": drop["product_name"],
                "competitor_name": drop["competitor_name"],
                "url": drop["url"],
                "message": (
                    f"Price dropped {drop['drop_percent']}% "
                    f"(${drop['previous_price']:.2f} -> ${drop['current_price']:.2f})"
                ),
                "previous_price": drop["previous_price"],
                "current_price": drop["current_price"],
                "price_change_percent": -drop["drop_percent"],
            }
            airtable.save_alert(alert_data)
            alerts_saved += 1

        for change in stock_changes:
            if change["is_back_in_stock"]:
                alert_data = {
                    "alert_id": f"stock-{change['product_id']}-{payload.scraped_at.isoformat()}",
                    "alert_type": "back_in_stock",
                    "severity": "info",
                    "product_id": change["product_id"],
                    "product_name": change["product_name"],
                    "competitor_name": change["competitor_name"],
                    "url": change["url"],
                    "message": f"Product is back in stock at {change['competitor_name']}",
                }
                airtable.save_alert(alert_data)
                alerts_saved += 1

        return {
            "status": "processed",
            "total_products_received": payload.total_products,
            "sync_stats": sync_stats,
            "price_drops_detected": len(drops),
            "stock_changes_detected": len(stock_changes),
            "alerts_saved": alerts_saved,
        }

    except Exception as exc:
        logger.exception("Apify webhook processing failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
