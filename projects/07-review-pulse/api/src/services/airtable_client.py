"""Airtable client for persisting reviews and summaries."""

from __future__ import annotations

import logging
from typing import Any

from pyairtable import Api
from pyairtable.formulas import FIELD, STR_VALUE

from api.src.config import get_settings, Settings

logger = logging.getLogger(__name__)


class AirtableError(Exception):
    """Raised when an Airtable operation fails."""


class AirtableClient:
    """Thin wrapper around pyairtable for ReviewPulse tables."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._api = Api(self._settings.airtable_api_key)
        self._reviews_table = self._api.table(
            self._settings.airtable_base_id,
            self._settings.airtable_reviews_table,
        )
        self._sentiment_table = self._api.table(
            self._settings.airtable_base_id,
            self._settings.airtable_sentiment_table,
        )
        self._responses_table = self._api.table(
            self._settings.airtable_base_id,
            self._settings.airtable_responses_table,
        )

    # ------------------------------------------------------------------
    # Reviews
    # ------------------------------------------------------------------

    def save_review(self, review: dict[str, Any]) -> dict[str, Any]:
        """Save a single review record to Airtable.

        Args:
            review: Dictionary with review fields matching the Airtable schema.

        Returns:
            The created Airtable record.
        """
        try:
            fields = {
                "ReviewID": review.get("review_id", ""),
                "Platform": review.get("platform", ""),
                "BusinessID": review.get("business_id", ""),
                "BusinessName": review.get("business_name", ""),
                "ReviewerName": review.get("reviewer_name", "Anonymous"),
                "Rating": review.get("rating", 0),
                "Text": review.get("text", ""),
                "Date": review.get("date", ""),
                "ScrapedAt": review.get("scraped_at", ""),
                "Language": review.get("language", "en"),
            }
            record = self._reviews_table.create(fields)
            logger.info("Saved review %s to Airtable", review.get("review_id"))
            return record
        except Exception as exc:
            logger.error("Failed to save review: %s", exc)
            raise AirtableError(f"Failed to save review: {exc}") from exc

    def save_summary(self, summary: dict[str, Any]) -> dict[str, Any]:
        """Save a review summary / sentiment analysis result to Airtable.

        Args:
            summary: Dictionary with sentiment analysis fields.

        Returns:
            The created Airtable record.
        """
        try:
            fields = {
                "ReviewID": summary.get("review_id", ""),
                "OverallScore": summary.get("overall_score", 0),
                "Label": summary.get("label", "neutral"),
                "Confidence": summary.get("confidence", 0),
                "KeyPhrases": ", ".join(summary.get("key_phrases", [])),
                "Summary": summary.get("summary", ""),
                "ModelUsed": summary.get("model_used", ""),
                "AnalyzedAt": summary.get("analyzed_at", ""),
            }
            record = self._sentiment_table.create(fields)
            logger.info(
                "Saved sentiment summary for review %s",
                summary.get("review_id"),
            )
            return record
        except Exception as exc:
            logger.error("Failed to save summary: %s", exc)
            raise AirtableError(f"Failed to save summary: {exc}") from exc

    def get_reviews(
        self,
        filters: dict[str, str] | None = None,
        max_records: int = 100,
    ) -> list[dict[str, Any]]:
        """Retrieve reviews with optional filters.

        Args:
            filters: Optional dict of field-name -> value pairs used to
                     construct an Airtable formula.
            max_records: Maximum number of records to return.

        Returns:
            List of Airtable record dictionaries.
        """
        try:
            formula = None
            if filters:
                clauses = []
                for field, value in filters.items():
                    clauses.append(
                        FIELD(field).eq(STR_VALUE(value))
                    )
                if len(clauses) == 1:
                    formula = clauses[0]
                else:
                    formula = f"AND({', '.join(str(c) for c in clauses)})"

            records = self._reviews_table.all(
                formula=formula,
                max_records=max_records,
                sort=["-Date"],
            )
            return [
                {"id": r["id"], **r["fields"]}
                for r in records
            ]
        except Exception as exc:
            logger.error("Failed to fetch reviews: %s", exc)
            raise AirtableError(f"Failed to fetch reviews: {exc}") from exc

    def get_review_stats(self) -> dict[str, Any]:
        """Compute aggregate statistics across all reviews.

        Returns:
            Dictionary with total_reviews, average_rating,
            sentiment_breakdown, and reviews_by_platform.
        """
        try:
            records = self._reviews_table.all()
            sentiments = self._sentiment_table.all()

            total = len(records)
            ratings = [
                r["fields"].get("Rating", 0)
                for r in records
                if r["fields"].get("Rating") is not None
            ]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0.0

            # Sentiment breakdown
            sentiment_counts: dict[str, int] = {
                "positive": 0,
                "neutral": 0,
                "negative": 0,
            }
            for s in sentiments:
                label = s["fields"].get("Label", "neutral").lower()
                if label in sentiment_counts:
                    sentiment_counts[label] += 1

            # Reviews by platform
            platform_counts: dict[str, int] = {}
            for r in records:
                platform = r["fields"].get("Platform", "unknown")
                platform_counts[platform] = platform_counts.get(platform, 0) + 1

            return {
                "total_reviews": total,
                "average_rating": round(avg_rating, 2),
                "sentiment_breakdown": sentiment_counts,
                "reviews_by_platform": platform_counts,
            }
        except Exception as exc:
            logger.error("Failed to compute review stats: %s", exc)
            raise AirtableError(f"Failed to compute stats: {exc}") from exc

    def list_summaries(self, max_records: int = 50) -> list[dict[str, Any]]:
        """List stored sentiment analysis summaries.

        Args:
            max_records: Maximum number of records to return.

        Returns:
            List of summary records.
        """
        try:
            records = self._sentiment_table.all(
                max_records=max_records,
                sort=["-AnalyzedAt"],
            )
            return [
                {"id": r["id"], **r["fields"]}
                for r in records
            ]
        except Exception as exc:
            logger.error("Failed to list summaries: %s", exc)
            raise AirtableError(f"Failed to list summaries: {exc}") from exc
