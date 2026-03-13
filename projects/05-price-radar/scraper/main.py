"""
PriceRadar - Apify Actor for Competitor Price Monitoring

Scrapes product prices from e-commerce websites using configurable
CSS selectors. Supports multiple site patterns and handles common
e-commerce page structures.
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from apify import Actor
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("price-radar-scraper")

# Common e-commerce CSS selector patterns
DEFAULT_SELECTORS = {
    "generic": {
        "product_name": [
            "h1.product-title",
            "h1.product-name",
            "h1[itemprop='name']",
            ".product-info h1",
            "#productTitle",
            "[data-testid='product-title']",
        ],
        "price": [
            "[itemprop='price']",
            ".price-current",
            ".product-price .current",
            "#priceblock_ourprice",
            ".price--main",
            "[data-testid='product-price']",
            ".sale-price",
            ".regular-price",
        ],
        "availability": [
            "[itemprop='availability']",
            "#availability span",
            ".stock-status",
            ".availability-status",
            "[data-testid='availability']",
            ".product-availability",
        ],
        "image": [
            ".product-image img",
            "#main-image",
            "[itemprop='image']",
            ".gallery-image img:first-child",
        ],
        "sku": [
            "[itemprop='sku']",
            ".product-sku",
            "#product-sku",
            "[data-sku]",
        ],
    },
    "shopify": {
        "product_name": [".product__title", "h1.product-single__title"],
        "price": [".product__price", ".price__regular .price-item"],
        "availability": [".product__availability", ".product-form__submit"],
        "image": [".product__media img", ".product-single__photo img"],
        "sku": [".product__sku"],
    },
    "woocommerce": {
        "product_name": [".product_title.entry-title"],
        "price": [".woocommerce-Price-amount", "p.price ins .amount", "p.price .amount"],
        "availability": [".stock", ".in-stock", ".out-of-stock"],
        "image": [".woocommerce-product-gallery__image img"],
        "sku": [".sku"],
    },
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


def parse_price(price_text: str) -> Optional[float]:
    """Extract numeric price from text like '$29.99' or '29,99 EUR'."""
    if not price_text:
        return None

    cleaned = price_text.strip()
    # Remove currency symbols and whitespace
    cleaned = re.sub(r"[^\d.,]", "", cleaned)

    if not cleaned:
        return None

    # Handle European format (1.234,56) vs US format (1,234.56)
    if "," in cleaned and "." in cleaned:
        if cleaned.rindex(",") > cleaned.rindex("."):
            # European: 1.234,56
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            # US: 1,234.56
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        # Could be European decimal or US thousands
        parts = cleaned.split(",")
        if len(parts[-1]) == 2:
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")

    try:
        return round(float(cleaned), 2)
    except ValueError:
        return None


def detect_availability(text: str) -> str:
    """Determine product availability from status text."""
    if not text:
        return "unknown"

    lower = text.lower().strip()

    in_stock_patterns = ["in stock", "available", "in-stock", "add to cart", "buy now"]
    out_of_stock_patterns = [
        "out of stock",
        "unavailable",
        "sold out",
        "out-of-stock",
        "currently unavailable",
        "notify me",
    ]

    for pattern in out_of_stock_patterns:
        if pattern in lower:
            return "out_of_stock"

    for pattern in in_stock_patterns:
        if pattern in lower:
            return "in_stock"

    return "unknown"


def extract_with_selectors(soup: BeautifulSoup, selectors: list[str]) -> Optional[str]:
    """Try multiple CSS selectors and return the first match's text."""
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            # Check for content attribute (common in structured data)
            if element.get("content"):
                return element["content"]
            text = element.get_text(strip=True)
            if text:
                return text
    return None


def scrape_product(url: str, custom_selectors: Optional[dict] = None) -> Optional[dict]:
    """
    Scrape a single product page for price and availability data.

    Args:
        url: Product page URL
        custom_selectors: Optional dict with CSS selectors to override defaults

    Returns:
        Dict with product data or None if scraping failed
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Failed to fetch %s: %s", url, exc)
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Determine which selector set to use
    domain = urlparse(url).netloc.lower()
    selectors = DEFAULT_SELECTORS["generic"].copy()

    # Auto-detect platform
    page_html = response.text.lower()
    if "shopify" in page_html or ".myshopify.com" in domain:
        selectors.update(DEFAULT_SELECTORS["shopify"])
    elif "woocommerce" in page_html or "wc-" in page_html:
        selectors.update(DEFAULT_SELECTORS["woocommerce"])

    # Apply custom selectors (highest priority)
    if custom_selectors:
        for key, value in custom_selectors.items():
            if isinstance(value, str):
                selectors[key] = [value]
            elif isinstance(value, list):
                selectors[key] = value

    # Extract product data
    product_name = extract_with_selectors(soup, selectors.get("product_name", []))
    price_text = extract_with_selectors(soup, selectors.get("price", []))
    availability_text = extract_with_selectors(soup, selectors.get("availability", []))
    sku = extract_with_selectors(soup, selectors.get("sku", []))

    # Extract image URL
    image_url = None
    for img_selector in selectors.get("image", []):
        img_el = soup.select_one(img_selector)
        if img_el:
            image_url = img_el.get("src") or img_el.get("data-src")
            if image_url:
                image_url = urljoin(url, image_url)
                break

    # Try JSON-LD structured data as fallback
    json_ld = soup.find("script", type="application/ld+json")
    if json_ld:
        try:
            ld_data = json.loads(json_ld.string)
            if isinstance(ld_data, list):
                ld_data = next(
                    (d for d in ld_data if d.get("@type") == "Product"), ld_data[0]
                )

            if ld_data.get("@type") == "Product":
                if not product_name:
                    product_name = ld_data.get("name")
                if not sku:
                    sku = ld_data.get("sku")
                if not image_url:
                    image_url = ld_data.get("image")

                offers = ld_data.get("offers", {})
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                if not price_text:
                    price_text = str(offers.get("price", ""))
                if not availability_text:
                    avail = offers.get("availability", "")
                    if "InStock" in str(avail):
                        availability_text = "In Stock"
                    elif "OutOfStock" in str(avail):
                        availability_text = "Out of Stock"
        except (json.JSONDecodeError, IndexError, KeyError):
            pass

    price = parse_price(price_text) if price_text else None
    availability = detect_availability(availability_text)

    if not product_name and not price:
        logger.warning("Could not extract product data from %s", url)
        return None

    return {
        "url": url,
        "domain": domain,
        "product_name": product_name or "Unknown Product",
        "price": price,
        "price_text": price_text,
        "currency": detect_currency(price_text) if price_text else "USD",
        "availability": availability,
        "sku": sku,
        "image_url": image_url,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def detect_currency(price_text: str) -> str:
    """Detect currency from price text."""
    currency_map = {
        "$": "USD",
        "\u20ac": "EUR",
        "\u00a3": "GBP",
        "\u00a5": "JPY",
        "CAD": "CAD",
        "AUD": "AUD",
        "kr": "SEK",
        "CHF": "CHF",
    }
    for symbol, code in currency_map.items():
        if symbol in price_text:
            return code
    return "USD"


async def main() -> None:
    """Apify actor entry point."""
    async with Actor:
        actor_input = await Actor.get_input() or {}

        urls = actor_input.get("urls", [])
        custom_selectors = actor_input.get("selectors", {})
        webhook_url = actor_input.get("webhookUrl")
        competitor_name = actor_input.get("competitorName", "")
        request_delay = actor_input.get("requestDelay", 2)

        if not urls:
            logger.error("No URLs provided in input")
            await Actor.fail(status_message="No URLs provided")
            return

        logger.info("Starting price scrape for %d URLs", len(urls))

        results = []
        for i, url_entry in enumerate(urls):
            # Support both string URLs and objects with URL + selectors
            if isinstance(url_entry, str):
                url = url_entry
                page_selectors = custom_selectors
            else:
                url = url_entry.get("url", "")
                page_selectors = url_entry.get("selectors", custom_selectors)

            if not url:
                continue

            logger.info("[%d/%d] Scraping: %s", i + 1, len(urls), url)

            product_data = scrape_product(url, page_selectors)
            if product_data:
                product_data["competitor_name"] = (
                    url_entry.get("competitorName", competitor_name)
                    if isinstance(url_entry, dict)
                    else competitor_name
                )
                results.append(product_data)
                await Actor.push_data(product_data)
                logger.info(
                    "  Found: %s - %s (%s)",
                    product_data["product_name"],
                    product_data.get("price_text", "N/A"),
                    product_data["availability"],
                )
            else:
                logger.warning("  Failed to extract data from %s", url)

            # Rate limiting between requests
            if i < len(urls) - 1:
                await asyncio.sleep(request_delay)

        logger.info("Scraping complete. %d/%d products extracted.", len(results), len(urls))

        # Send results to webhook if configured
        if webhook_url and results:
            try:
                payload = {
                    "source": "apify-price-radar",
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "total_products": len(results),
                    "products": results,
                }
                resp = requests.post(webhook_url, json=payload, timeout=30)
                resp.raise_for_status()
                logger.info("Results sent to webhook: %s", webhook_url)
            except requests.RequestException as exc:
                logger.error("Failed to send webhook: %s", exc)

        await Actor.set_status_message(
            f"Scraped {len(results)}/{len(urls)} products successfully"
        )


if __name__ == "__main__":
    asyncio.run(main())
