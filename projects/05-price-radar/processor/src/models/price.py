"""Pydantic models for PriceRadar price monitoring system."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class AvailabilityStatus(str, Enum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    UNKNOWN = "unknown"


class AlertType(str, Enum):
    PRICE_DROP = "price_drop"
    PRICE_INCREASE = "price_increase"
    NEW_LOWEST = "new_lowest"
    BACK_IN_STOCK = "back_in_stock"
    OUT_OF_STOCK = "out_of_stock"
    THRESHOLD_CROSSED = "threshold_crossed"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# --- Core Models ---


class PriceRecord(BaseModel):
    """A single price observation from a scrape."""

    url: str
    domain: str
    product_name: str
    price: Optional[float] = None
    price_text: Optional[str] = None
    currency: str = "USD"
    availability: AvailabilityStatus = AvailabilityStatus.UNKNOWN
    sku: Optional[str] = None
    image_url: Optional[str] = None
    competitor_name: str = ""
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class CompetitorProduct(BaseModel):
    """A product tracked across one competitor."""

    product_id: str = Field(description="Internal product identifier")
    competitor_name: str
    product_name: str
    url: str
    current_price: Optional[float] = None
    currency: str = "USD"
    availability: AvailabilityStatus = AvailabilityStatus.UNKNOWN
    sku: Optional[str] = None
    image_url: Optional[str] = None
    category: str = ""
    tags: list[str] = Field(default_factory=list)
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    average_price: Optional[float] = None


class PriceHistory(BaseModel):
    """Price history for a specific product."""

    product_id: str
    product_name: str
    competitor_name: str
    url: str
    records: list[dict] = Field(
        default_factory=list,
        description="List of {price, availability, scraped_at} entries",
    )
    current_price: Optional[float] = None
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    average_price: Optional[float] = None
    price_change_30d: Optional[float] = Field(
        None, description="Price change percentage over last 30 days"
    )
    total_observations: int = 0


class PriceAlertRule(BaseModel):
    """Configuration for an alert trigger."""

    rule_id: str = ""
    product_id: Optional[str] = Field(None, description="Specific product or None for all")
    alert_type: AlertType
    threshold_percent: Optional[float] = Field(
        None, description="Percentage threshold for price change alerts"
    )
    threshold_price: Optional[float] = Field(
        None, description="Absolute price threshold"
    )
    enabled: bool = True


class PriceAlert(BaseModel):
    """A triggered price alert."""

    alert_id: str = Field(default="", description="Unique alert identifier")
    alert_type: AlertType
    severity: AlertSeverity = AlertSeverity.INFO
    product_id: str
    product_name: str
    competitor_name: str
    url: str
    message: str
    previous_price: Optional[float] = None
    current_price: Optional[float] = None
    price_change_percent: Optional[float] = None
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False


# --- API Request/Response Models ---


class PriceWebhookPayload(BaseModel):
    """Payload received from Apify scraper webhook."""

    source: str = "apify-price-radar"
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    total_products: int = 0
    products: list[PriceRecord]


class PriceComparisonRequest(BaseModel):
    """Request to compare prices across competitors."""

    product_name: Optional[str] = None
    sku: Optional[str] = None
    urls: list[str] = Field(default_factory=list)
    include_history: bool = False


class CompetitorPriceEntry(BaseModel):
    """Price from a single competitor in a comparison."""

    competitor_name: str
    price: Optional[float]
    currency: str = "USD"
    availability: AvailabilityStatus
    url: str
    last_updated: datetime


class PriceComparisonResult(BaseModel):
    """Result of a cross-competitor price comparison."""

    product_name: str
    sku: Optional[str] = None
    competitors: list[CompetitorPriceEntry]
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
    average_price: Optional[float] = None
    best_deal: Optional[CompetitorPriceEntry] = None
    price_spread_percent: Optional[float] = Field(
        None, description="Percentage difference between lowest and highest price"
    )


class DailyReportProduct(BaseModel):
    """Product entry in the daily report."""

    product_name: str
    competitor_name: str
    current_price: Optional[float]
    previous_price: Optional[float]
    price_change: Optional[float]
    price_change_percent: Optional[float]
    availability: AvailabilityStatus
    url: str


class DailyReport(BaseModel):
    """Daily price monitoring summary report."""

    report_date: datetime = Field(default_factory=datetime.utcnow)
    total_products_monitored: int = 0
    total_competitors: int = 0
    price_drops: list[DailyReportProduct] = Field(default_factory=list)
    price_increases: list[DailyReportProduct] = Field(default_factory=list)
    new_lowest_prices: list[DailyReportProduct] = Field(default_factory=list)
    stock_changes: list[DailyReportProduct] = Field(default_factory=list)
    alerts_triggered: int = 0
    summary: str = ""
