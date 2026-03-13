"""
ReviewPulse - Apify Actor for Multi-Platform Review Scraping

Scrapes reviews from Google Maps, Yelp, and Trustpilot.
Extracts: reviewer name, rating, text, date, platform, business name.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from apify import Actor
from httpx import AsyncClient
from selectolax.parser import HTMLParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("review-pulse-scraper")

# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _review_id(platform: str, reviewer: str, date_str: str, text: str) -> str:
    """Generate a deterministic review ID for deduplication."""
    raw = f"{platform}:{reviewer}:{date_str}:{text[:80]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _normalise_date(raw: str) -> str:
    """Best-effort ISO-8601 date normalisation."""
    raw = raw.strip()
    for fmt in (
        "%Y-%m-%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
    ):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # Relative dates (e.g. "2 days ago")
    match = re.match(r"(\d+)\s+(day|week|month|year)s?\s+ago", raw, re.I)
    if match:
        num, unit = int(match.group(1)), match.group(2).lower()
        from dateutil.relativedelta import relativedelta

        delta_map = {
            "day": relativedelta(days=num),
            "week": relativedelta(weeks=num),
            "month": relativedelta(months=num),
            "year": relativedelta(years=num),
        }
        return (datetime.now(timezone.utc) - delta_map[unit]).strftime("%Y-%m-%d")
    return raw


# ---------------------------------------------------------------------------
# Platform scrapers
# ---------------------------------------------------------------------------

class GoogleMapsScraper:
    """Scrape Google Maps reviews via the unofficial sort-by-newest URL."""

    PLATFORM = "google_maps"

    def __init__(self, client: AsyncClient) -> None:
        self.client = client

    async def scrape(self, url: str, max_reviews: int = 100) -> list[dict[str, Any]]:
        logger.info("Scraping Google Maps: %s", url)
        reviews: list[dict[str, Any]] = []

        try:
            resp = await self.client.get(url, follow_redirects=True, timeout=30)
            resp.raise_for_status()
            tree = HTMLParser(resp.text)

            business_name = ""
            title_el = tree.css_first("meta[property='og:title']")
            if title_el:
                business_name = title_el.attributes.get("content", "").split(" - ")[0]

            review_nodes = tree.css("[data-review-id]")
            for node in review_nodes[:max_reviews]:
                reviewer_el = node.css_first("[class*='author']")
                rating_el = node.css_first("[aria-label*='star']")
                text_el = node.css_first("[class*='review-text'], .review-full-text")
                date_el = node.css_first("[class*='date'], [class*='timestamp']")

                reviewer = reviewer_el.text(strip=True) if reviewer_el else "Anonymous"
                rating_text = rating_el.attributes.get("aria-label", "") if rating_el else ""
                rating_match = re.search(r"(\d+(\.\d+)?)", rating_text)
                rating = float(rating_match.group(1)) if rating_match else 0.0
                text = text_el.text(strip=True) if text_el else ""
                date_raw = date_el.text(strip=True) if date_el else ""

                review = {
                    "review_id": _review_id(self.PLATFORM, reviewer, date_raw, text),
                    "platform": self.PLATFORM,
                    "business_name": business_name,
                    "business_url": url,
                    "reviewer_name": reviewer,
                    "rating": rating,
                    "max_rating": 5.0,
                    "text": text,
                    "date": _normalise_date(date_raw),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "language": "en",
                }
                reviews.append(review)

        except Exception:
            logger.exception("Error scraping Google Maps")

        logger.info("Google Maps: collected %d reviews", len(reviews))
        return reviews


class YelpScraper:
    """Scrape Yelp business reviews."""

    PLATFORM = "yelp"

    def __init__(self, client: AsyncClient) -> None:
        self.client = client

    async def scrape(self, url: str, max_reviews: int = 100) -> list[dict[str, Any]]:
        logger.info("Scraping Yelp: %s", url)
        reviews: list[dict[str, Any]] = []

        try:
            resp = await self.client.get(url, follow_redirects=True, timeout=30)
            resp.raise_for_status()
            tree = HTMLParser(resp.text)

            business_name = ""
            h1 = tree.css_first("h1")
            if h1:
                business_name = h1.text(strip=True)

            review_nodes = tree.css("[data-testid='review'], .review, li[class*='review']")
            for node in review_nodes[:max_reviews]:
                reviewer_el = node.css_first(
                    "[class*='user-name'], a[href*='/user_details']"
                )
                rating_el = node.css_first(
                    "[aria-label*='star'], [class*='star-rating'] div"
                )
                text_el = node.css_first("[class*='comment'], [lang='en'] span, p")
                date_el = node.css_first("[class*='date'], span[class*='css-']")

                reviewer = reviewer_el.text(strip=True) if reviewer_el else "Anonymous"
                rating = 0.0
                if rating_el:
                    lbl = rating_el.attributes.get("aria-label", "")
                    m = re.search(r"(\d+(\.\d+)?)", lbl)
                    if m:
                        rating = float(m.group(1))
                text = text_el.text(strip=True) if text_el else ""
                date_raw = date_el.text(strip=True) if date_el else ""

                review = {
                    "review_id": _review_id(self.PLATFORM, reviewer, date_raw, text),
                    "platform": self.PLATFORM,
                    "business_name": business_name,
                    "business_url": url,
                    "reviewer_name": reviewer,
                    "rating": rating,
                    "max_rating": 5.0,
                    "text": text,
                    "date": _normalise_date(date_raw),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "language": "en",
                }
                reviews.append(review)

        except Exception:
            logger.exception("Error scraping Yelp")

        logger.info("Yelp: collected %d reviews", len(reviews))
        return reviews


class TrustpilotScraper:
    """Scrape Trustpilot business reviews."""

    PLATFORM = "trustpilot"

    def __init__(self, client: AsyncClient) -> None:
        self.client = client

    async def scrape(self, url: str, max_reviews: int = 100) -> list[dict[str, Any]]:
        logger.info("Scraping Trustpilot: %s", url)
        reviews: list[dict[str, Any]] = []

        try:
            pages = (max_reviews // 20) + 1
            for page in range(1, pages + 1):
                page_url = f"{url.rstrip('/')}?page={page}"
                resp = await self.client.get(
                    page_url, follow_redirects=True, timeout=30
                )
                resp.raise_for_status()
                tree = HTMLParser(resp.text)

                if page == 1:
                    business_name = ""
                    title_el = tree.css_first(
                        "[data-business-unit-name], .multi-size-header__big"
                    )
                    if title_el:
                        business_name = (
                            title_el.attributes.get("data-business-unit-name", "")
                            or title_el.text(strip=True)
                        )

                review_cards = tree.css(
                    "article.review, [data-service-review-card-paper]"
                )
                if not review_cards:
                    break

                for card in review_cards:
                    reviewer_el = card.css_first(
                        "[data-consumer-name-typography], .consumer-information__name"
                    )
                    rating_el = card.css_first("[data-service-review-rating]")
                    text_el = card.css_first(
                        "[data-service-review-text-typography], .review-content__text"
                    )
                    date_el = card.css_first("time")

                    reviewer = (
                        reviewer_el.text(strip=True) if reviewer_el else "Anonymous"
                    )
                    rating = 0.0
                    if rating_el:
                        r = rating_el.attributes.get(
                            "data-service-review-rating", ""
                        )
                        try:
                            rating = float(r)
                        except ValueError:
                            pass
                    text = text_el.text(strip=True) if text_el else ""
                    date_raw = (
                        date_el.attributes.get("datetime", "")
                        if date_el
                        else ""
                    )

                    review = {
                        "review_id": _review_id(
                            self.PLATFORM, reviewer, date_raw, text
                        ),
                        "platform": self.PLATFORM,
                        "business_name": business_name,
                        "business_url": url,
                        "reviewer_name": reviewer,
                        "rating": rating,
                        "max_rating": 5.0,
                        "text": text,
                        "date": _normalise_date(date_raw),
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                        "language": "en",
                    }
                    reviews.append(review)

                    if len(reviews) >= max_reviews:
                        break

                if len(reviews) >= max_reviews:
                    break

        except Exception:
            logger.exception("Error scraping Trustpilot")

        logger.info("Trustpilot: collected %d reviews", len(reviews))
        return reviews


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

PLATFORM_MAP: dict[str, type] = {
    "google": GoogleMapsScraper,
    "yelp": YelpScraper,
    "trustpilot": TrustpilotScraper,
}


def _detect_platform(url: str) -> str | None:
    host = urlparse(url).hostname or ""
    for key in PLATFORM_MAP:
        if key in host:
            return key
    return None


# ---------------------------------------------------------------------------
# Main actor
# ---------------------------------------------------------------------------

async def main() -> None:
    async with Actor:
        actor_input: dict[str, Any] = await Actor.get_input() or {}

        urls: list[str] = actor_input.get("urls", [])
        max_reviews: int = actor_input.get("maxReviews", 100)
        webhook_url: str | None = actor_input.get("webhookUrl")
        business_id: str = actor_input.get("businessId", "")

        if not urls:
            logger.error("No URLs provided in actor input")
            await Actor.fail(status_message="No URLs provided")
            return

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

        all_reviews: list[dict[str, Any]] = []

        async with AsyncClient(headers=headers) as client:
            for url in urls:
                platform_key = _detect_platform(url)
                if not platform_key:
                    logger.warning("Unsupported platform URL: %s", url)
                    continue

                scraper_cls = PLATFORM_MAP[platform_key]
                scraper = scraper_cls(client)
                reviews = await scraper.scrape(url, max_reviews=max_reviews)

                for review in reviews:
                    review["business_id"] = business_id
                    await Actor.push_data(review)
                    all_reviews.append(review)

            # Send to webhook if configured
            if webhook_url and all_reviews:
                payload = {
                    "business_id": business_id,
                    "reviews": all_reviews,
                    "total_count": len(all_reviews),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                }
                try:
                    resp = await client.post(
                        webhook_url, json=payload, timeout=30
                    )
                    logger.info(
                        "Webhook response: %d %s", resp.status_code, resp.text[:200]
                    )
                except Exception:
                    logger.exception("Failed to send webhook")

        logger.info(
            "Scraping complete. Total reviews collected: %d", len(all_reviews)
        )


if __name__ == "__main__":
    asyncio.run(main())
