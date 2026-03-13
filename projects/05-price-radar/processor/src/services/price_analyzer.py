"""
Price analysis service for PriceRadar.

Handles price comparison logic, trend detection, drop identification,
and deal scoring across competitors.
"""

import logging
import statistics
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional

from ..models.price import (
    AvailabilityStatus,
    CompetitorPriceEntry,
    DailyReport,
    DailyReportProduct,
    PriceComparisonResult,
    PriceHistory,
    PriceRecord,
)
from .airtable_sync import AirtableSync

logger = logging.getLogger("price-radar.analyzer")


class PriceAnalyzer:
    """Analyzes price data across competitors and over time."""

    def __init__(self, airtable: AirtableSync):
        self.airtable = airtable

    def get_price_history(self, product_id: str) -> Optional[PriceHistory]:
        """Retrieve and compute price history statistics for a product."""
        product = self.airtable.get_product(product_id)
        if not product:
            return None

        history_records = self.airtable.get_price_history(product_id)
        prices = [r["price"] for r in history_records if r.get("price") is not None]

        history = PriceHistory(
            product_id=product_id,
            product_name=product.get("Product Name", ""),
            competitor_name=product.get("Competitor", ""),
            url=product.get("URL", ""),
            records=history_records,
            current_price=prices[-1] if prices else None,
            total_observations=len(history_records),
        )

        if prices:
            history.lowest_price = min(prices)
            history.highest_price = max(prices)
            history.average_price = round(statistics.mean(prices), 2)

            # Calculate 30-day price change
            thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
            recent = [
                r for r in history_records
                if r.get("scraped_at") and _parse_dt(r["scraped_at"]) >= thirty_days_ago
            ]
            if recent and len(recent) >= 2:
                old_price = recent[0].get("price")
                new_price = recent[-1].get("price")
                if old_price and new_price and old_price > 0:
                    history.price_change_30d = round(
                        ((new_price - old_price) / old_price) * 100, 2
                    )

        return history

    def compare_prices(
        self,
        product_name: Optional[str] = None,
        sku: Optional[str] = None,
        urls: Optional[list[str]] = None,
    ) -> Optional[PriceComparisonResult]:
        """
        Compare prices for the same product across different competitors.

        Matches products by name, SKU, or specific URLs.
        """
        matching_products = self.airtable.find_products(
            product_name=product_name, sku=sku, urls=urls
        )

        if not matching_products:
            return None

        competitors = []
        for product in matching_products:
            entry = CompetitorPriceEntry(
                competitor_name=product.get("Competitor", "Unknown"),
                price=product.get("Current Price"),
                currency=product.get("Currency", "USD"),
                availability=AvailabilityStatus(
                    product.get("Availability", "unknown")
                ),
                url=product.get("URL", ""),
                last_updated=_parse_dt(
                    product.get("Last Updated", datetime.now(timezone.utc).isoformat())
                ),
            )
            competitors.append(entry)

        # Compute comparison statistics
        available_prices = [
            c.price for c in competitors
            if c.price is not None and c.availability == AvailabilityStatus.IN_STOCK
        ]

        result = PriceComparisonResult(
            product_name=product_name or matching_products[0].get("Product Name", ""),
            sku=sku,
            competitors=competitors,
        )

        if available_prices:
            result.lowest_price = min(available_prices)
            result.highest_price = max(available_prices)
            result.average_price = round(statistics.mean(available_prices), 2)

            # Find best deal (lowest price that's in stock)
            result.best_deal = min(
                [c for c in competitors if c.price is not None
                 and c.availability == AvailabilityStatus.IN_STOCK],
                key=lambda c: c.price,
                default=None,
            )

            if result.lowest_price and result.highest_price and result.lowest_price > 0:
                result.price_spread_percent = round(
                    ((result.highest_price - result.lowest_price) / result.lowest_price)
                    * 100,
                    2,
                )

        return result

    def detect_price_drops(
        self, records: list[PriceRecord], min_drop_percent: float = 5.0
    ) -> list[dict]:
        """
        Detect significant price drops by comparing new records against stored history.

        Returns list of dicts with product info and drop details.
        """
        drops = []

        for record in records:
            if record.price is None:
                continue

            product_id = self.airtable.find_product_id(
                url=record.url, competitor=record.competitor_name
            )
            if not product_id:
                continue

            previous = self.airtable.get_latest_price(product_id)
            if previous is None or previous <= 0:
                continue

            change_percent = ((record.price - previous) / previous) * 100

            if change_percent <= -min_drop_percent:
                drops.append({
                    "product_id": product_id,
                    "product_name": record.product_name,
                    "competitor_name": record.competitor_name,
                    "url": record.url,
                    "previous_price": previous,
                    "current_price": record.price,
                    "drop_percent": round(abs(change_percent), 2),
                    "drop_amount": round(previous - record.price, 2),
                })

        return drops

    def detect_stock_changes(self, records: list[PriceRecord]) -> list[dict]:
        """Detect products that changed stock status (back in stock / out of stock)."""
        changes = []

        for record in records:
            product_id = self.airtable.find_product_id(
                url=record.url, competitor=record.competitor_name
            )
            if not product_id:
                continue

            previous_status = self.airtable.get_latest_availability(product_id)
            if previous_status is None:
                continue

            current = record.availability.value if hasattr(record.availability, "value") else str(record.availability)

            if previous_status != current:
                changes.append({
                    "product_id": product_id,
                    "product_name": record.product_name,
                    "competitor_name": record.competitor_name,
                    "url": record.url,
                    "previous_status": previous_status,
                    "current_status": current,
                    "is_back_in_stock": (
                        previous_status == "out_of_stock" and current == "in_stock"
                    ),
                })

        return changes

    def calculate_trend(self, prices: list[float], window: int = 7) -> str:
        """
        Determine price trend direction from a series of prices.

        Returns: 'rising', 'falling', 'stable', or 'volatile'
        """
        if len(prices) < 2:
            return "stable"

        recent = prices[-window:] if len(prices) >= window else prices

        if len(recent) < 2:
            return "stable"

        # Simple linear regression direction
        n = len(recent)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(recent)

        numerator = sum((i - x_mean) * (p - y_mean) for i, p in enumerate(recent))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable"

        slope = numerator / denominator
        relative_slope = slope / y_mean if y_mean != 0 else 0

        # Check volatility
        if len(recent) >= 3:
            try:
                cv = statistics.stdev(recent) / y_mean if y_mean != 0 else 0
                if cv > 0.15:
                    return "volatile"
            except statistics.StatisticsError:
                pass

        if relative_slope > 0.01:
            return "rising"
        elif relative_slope < -0.01:
            return "falling"
        return "stable"

    def generate_daily_report(self) -> DailyReport:
        """Generate a daily summary of all price monitoring activity."""
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)

        all_products = self.airtable.get_all_products()
        recent_history = self.airtable.get_recent_history(since=yesterday)

        # Group by product for analysis
        product_changes: dict[str, list[dict]] = defaultdict(list)
        for entry in recent_history:
            pid = entry.get("product_id", "")
            if pid:
                product_changes[pid].append(entry)

        report = DailyReport(
            report_date=now,
            total_products_monitored=len(all_products),
            total_competitors=len(
                set(p.get("Competitor", "") for p in all_products)
            ),
        )

        for product in all_products:
            pid = product.get("product_id", "")
            changes = product_changes.get(pid, [])
            if len(changes) < 2:
                continue

            old_entry = changes[0]
            new_entry = changes[-1]
            old_price = old_entry.get("price")
            new_price = new_entry.get("price")

            if old_price is None or new_price is None:
                continue

            change = new_price - old_price
            change_pct = (change / old_price * 100) if old_price > 0 else 0

            report_product = DailyReportProduct(
                product_name=product.get("Product Name", ""),
                competitor_name=product.get("Competitor", ""),
                current_price=new_price,
                previous_price=old_price,
                price_change=round(change, 2),
                price_change_percent=round(change_pct, 2),
                availability=AvailabilityStatus(
                    product.get("Availability", "unknown")
                ),
                url=product.get("URL", ""),
            )

            if change < 0:
                report.price_drops.append(report_product)

                # Check if this is a new all-time low
                history = self.airtable.get_price_history(pid)
                all_prices = [r["price"] for r in history if r.get("price") is not None]
                if all_prices and new_price <= min(all_prices):
                    report.new_lowest_prices.append(report_product)
            elif change > 0:
                report.price_increases.append(report_product)

            # Check stock changes
            old_avail = old_entry.get("availability", "unknown")
            new_avail = new_entry.get("availability", "unknown")
            if old_avail != new_avail:
                report.stock_changes.append(report_product)

        # Sort by magnitude of change
        report.price_drops.sort(
            key=lambda p: abs(p.price_change_percent or 0), reverse=True
        )
        report.price_increases.sort(
            key=lambda p: abs(p.price_change_percent or 0), reverse=True
        )

        # Generate summary text
        parts = []
        parts.append(
            f"Monitoring {report.total_products_monitored} products "
            f"across {report.total_competitors} competitors."
        )
        if report.price_drops:
            parts.append(f"{len(report.price_drops)} price drop(s) detected.")
        if report.price_increases:
            parts.append(f"{len(report.price_increases)} price increase(s) detected.")
        if report.new_lowest_prices:
            parts.append(
                f"{len(report.new_lowest_prices)} new all-time low price(s)!"
            )
        if report.stock_changes:
            parts.append(f"{len(report.stock_changes)} stock status change(s).")
        if not report.price_drops and not report.price_increases:
            parts.append("No significant price changes in the last 24 hours.")

        report.summary = " ".join(parts)
        return report

    def find_best_deals(self, top_n: int = 10) -> list[dict]:
        """Find products with the largest price drops from their historical average."""
        all_products = self.airtable.get_all_products()
        deals = []

        for product in all_products:
            pid = product.get("product_id", "")
            current = product.get("Current Price")
            if current is None or current <= 0:
                continue

            history = self.airtable.get_price_history(pid)
            prices = [r["price"] for r in history if r.get("price") is not None]
            if len(prices) < 3:
                continue

            avg = statistics.mean(prices)
            if avg <= 0:
                continue

            discount_pct = ((avg - current) / avg) * 100
            if discount_pct > 0:
                deals.append({
                    "product_id": pid,
                    "product_name": product.get("Product Name", ""),
                    "competitor_name": product.get("Competitor", ""),
                    "url": product.get("URL", ""),
                    "current_price": current,
                    "average_price": round(avg, 2),
                    "discount_percent": round(discount_pct, 2),
                    "availability": product.get("Availability", "unknown"),
                })

        deals.sort(key=lambda d: d["discount_percent"], reverse=True)
        return deals[:top_n]


def _parse_dt(dt_str: str) -> datetime:
    """Parse an ISO datetime string, handling multiple formats."""
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return datetime.now(timezone.utc)
