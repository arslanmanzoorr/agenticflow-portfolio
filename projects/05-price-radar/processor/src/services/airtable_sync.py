"""
Airtable synchronization service for PriceRadar.

Manages product and price history data in Airtable, providing
a persistent store for price monitoring with full history tracking.
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

from pyairtable import Api

from ..config import settings
from ..models.price import PriceRecord

logger = logging.getLogger("price-radar.airtable")


class AirtableSync:
    """Syncs price data to Airtable with history tracking."""

    def __init__(self):
        self.api = Api(settings.AIRTABLE_API_KEY)
        self.base = self.api.base(settings.AIRTABLE_BASE_ID)

        # Table references
        self.products_table = self.base.table(settings.AIRTABLE_PRODUCTS_TABLE)
        self.history_table = self.base.table(settings.AIRTABLE_HISTORY_TABLE)
        self.competitors_table = self.base.table(settings.AIRTABLE_COMPETITORS_TABLE)
        self.alerts_table = self.base.table(settings.AIRTABLE_ALERTS_TABLE)

    @staticmethod
    def generate_product_id(url: str, competitor: str) -> str:
        """Generate a deterministic product ID from URL and competitor name."""
        key = f"{competitor.lower().strip()}:{url.strip()}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def sync_price_records(self, records: list[PriceRecord]) -> dict:
        """
        Sync a batch of scraped price records to Airtable.

        For each record:
        1. Upsert the product in the Products table
        2. Append a price history entry
        3. Upsert the competitor if new

        Returns summary stats.
        """
        stats = {
            "products_created": 0,
            "products_updated": 0,
            "history_entries": 0,
            "competitors_synced": 0,
            "errors": 0,
        }

        # Track unique competitors in this batch
        seen_competitors: set[str] = set()

        for record in records:
            try:
                product_id = self.generate_product_id(
                    record.url, record.competitor_name
                )

                # Upsert product
                existing = self._find_product_by_id(product_id)
                product_fields = {
                    "Product ID": product_id,
                    "Product Name": record.product_name,
                    "URL": record.url,
                    "Competitor": record.competitor_name,
                    "Domain": record.domain,
                    "Current Price": record.price,
                    "Currency": record.currency,
                    "Availability": record.availability.value
                    if hasattr(record.availability, "value")
                    else str(record.availability),
                    "SKU": record.sku or "",
                    "Image URL": record.image_url or "",
                    "Last Updated": datetime.now(timezone.utc).isoformat(),
                }

                if existing:
                    # Update price stats
                    prev_lowest = existing["fields"].get("Lowest Price")
                    prev_highest = existing["fields"].get("Highest Price")

                    if record.price is not None:
                        if prev_lowest is None or record.price < prev_lowest:
                            product_fields["Lowest Price"] = record.price
                        if prev_highest is None or record.price > prev_highest:
                            product_fields["Highest Price"] = record.price

                    self.products_table.update(existing["id"], product_fields)
                    stats["products_updated"] += 1
                else:
                    # New product
                    product_fields["First Seen"] = datetime.now(
                        timezone.utc
                    ).isoformat()
                    if record.price is not None:
                        product_fields["Lowest Price"] = record.price
                        product_fields["Highest Price"] = record.price
                    self.products_table.create(product_fields)
                    stats["products_created"] += 1

                # Add price history entry
                history_fields = {
                    "Product ID": product_id,
                    "Product Name": record.product_name,
                    "Competitor": record.competitor_name,
                    "Price": record.price,
                    "Currency": record.currency,
                    "Availability": record.availability.value
                    if hasattr(record.availability, "value")
                    else str(record.availability),
                    "Scraped At": record.scraped_at.isoformat()
                    if isinstance(record.scraped_at, datetime)
                    else str(record.scraped_at),
                    "URL": record.url,
                }
                self.history_table.create(history_fields)
                stats["history_entries"] += 1

                # Track competitor
                if record.competitor_name and record.competitor_name not in seen_competitors:
                    seen_competitors.add(record.competitor_name)
                    self._upsert_competitor(record.competitor_name, record.domain)
                    stats["competitors_synced"] += 1

            except Exception as exc:
                logger.error(
                    "Error syncing record for %s: %s", record.url, exc, exc_info=True
                )
                stats["errors"] += 1

        logger.info(
            "Airtable sync complete: %d created, %d updated, %d history entries, %d errors",
            stats["products_created"],
            stats["products_updated"],
            stats["history_entries"],
            stats["errors"],
        )
        return stats

    def _find_product_by_id(self, product_id: str) -> Optional[dict]:
        """Find a product record by its product ID."""
        results = self.products_table.all(
            formula=f"{{Product ID}} = '{product_id}'"
        )
        return results[0] if results else None

    def _upsert_competitor(self, name: str, domain: str) -> None:
        """Create or update a competitor record."""
        existing = self.competitors_table.all(
            formula=f"{{Name}} = '{name}'"
        )
        fields = {
            "Name": name,
            "Domain": domain,
            "Last Scraped": datetime.now(timezone.utc).isoformat(),
        }
        if existing:
            # Increment scrape count
            current_count = existing[0]["fields"].get("Total Scrapes", 0)
            fields["Total Scrapes"] = current_count + 1
            self.competitors_table.update(existing[0]["id"], fields)
        else:
            fields["Total Scrapes"] = 1
            fields["Added On"] = datetime.now(timezone.utc).isoformat()
            self.competitors_table.create(fields)

    def get_product(self, product_id: str) -> Optional[dict]:
        """Get a product by ID, returning the Airtable fields."""
        record = self._find_product_by_id(product_id)
        return record["fields"] if record else None

    def get_all_products(self) -> list[dict]:
        """Get all tracked products."""
        records = self.products_table.all()
        return [
            {**r["fields"], "product_id": r["fields"].get("Product ID", "")}
            for r in records
        ]

    def get_price_history(self, product_id: str) -> list[dict]:
        """Get all price history entries for a product, sorted by date."""
        records = self.history_table.all(
            formula=f"{{Product ID}} = '{product_id}'",
            sort=["Scraped At"],
        )
        return [
            {
                "price": r["fields"].get("Price"),
                "availability": r["fields"].get("Availability", "unknown"),
                "scraped_at": r["fields"].get("Scraped At", ""),
                "currency": r["fields"].get("Currency", "USD"),
            }
            for r in records
        ]

    def get_recent_history(self, since: datetime) -> list[dict]:
        """Get all price history entries since a given datetime."""
        iso_since = since.isoformat()
        records = self.history_table.all(
            formula=f"IS_AFTER({{Scraped At}}, '{iso_since}')",
            sort=["Scraped At"],
        )
        return [
            {
                "product_id": r["fields"].get("Product ID", ""),
                "price": r["fields"].get("Price"),
                "availability": r["fields"].get("Availability", "unknown"),
                "scraped_at": r["fields"].get("Scraped At", ""),
            }
            for r in records
        ]

    def get_latest_price(self, product_id: str) -> Optional[float]:
        """Get the most recent price for a product."""
        product = self.get_product(product_id)
        if product:
            return product.get("Current Price")
        return None

    def get_latest_availability(self, product_id: str) -> Optional[str]:
        """Get the most recent availability status for a product."""
        product = self.get_product(product_id)
        if product:
            return product.get("Availability")
        return None

    def find_product_id(self, url: str, competitor: str) -> Optional[str]:
        """Find a product ID by URL and competitor name."""
        product_id = self.generate_product_id(url, competitor)
        if self._find_product_by_id(product_id):
            return product_id
        return None

    def find_products(
        self,
        product_name: Optional[str] = None,
        sku: Optional[str] = None,
        urls: Optional[list[str]] = None,
    ) -> list[dict]:
        """Find products matching any of the given criteria."""
        formulas = []

        if product_name:
            formulas.append(
                f"FIND(LOWER('{product_name}'), LOWER({{Product Name}}))"
            )
        if sku:
            formulas.append(f"{{SKU}} = '{sku}'")
        if urls:
            url_conditions = [f"{{URL}} = '{url}'" for url in urls]
            formulas.append(f"OR({', '.join(url_conditions)})")

        if not formulas:
            return []

        formula = f"OR({', '.join(formulas)})" if len(formulas) > 1 else formulas[0]
        records = self.products_table.all(formula=formula)
        return [r["fields"] for r in records]

    def save_alert(self, alert_data: dict) -> str:
        """Save a triggered alert to Airtable. Returns the record ID."""
        record = self.alerts_table.create({
            "Alert ID": alert_data.get("alert_id", ""),
            "Alert Type": alert_data.get("alert_type", ""),
            "Severity": alert_data.get("severity", "info"),
            "Product ID": alert_data.get("product_id", ""),
            "Product Name": alert_data.get("product_name", ""),
            "Competitor": alert_data.get("competitor_name", ""),
            "URL": alert_data.get("url", ""),
            "Message": alert_data.get("message", ""),
            "Previous Price": alert_data.get("previous_price"),
            "Current Price": alert_data.get("current_price"),
            "Price Change %": alert_data.get("price_change_percent"),
            "Triggered At": alert_data.get(
                "triggered_at", datetime.now(timezone.utc).isoformat()
            ),
            "Acknowledged": False,
        })
        return record["id"]

    def get_active_alerts(self, limit: int = 50) -> list[dict]:
        """Get unacknowledged alerts, most recent first."""
        records = self.alerts_table.all(
            formula="{Acknowledged} = FALSE()",
            sort=["-Triggered At"],
            max_records=limit,
        )
        return [r["fields"] for r in records]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged."""
        records = self.alerts_table.all(
            formula=f"{{Alert ID}} = '{alert_id}'"
        )
        if records:
            self.alerts_table.update(records[0]["id"], {"Acknowledged": True})
            return True
        return False
