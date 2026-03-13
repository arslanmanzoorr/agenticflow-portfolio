# PriceRadar - Competitor Price Monitoring System

Automated competitor price monitoring pipeline that scrapes product prices with Apify, analyzes trends with Python, stores history in Airtable, and delivers alerts via Email and Slack -- all orchestrated by n8n.

## Architecture

```
[Apify Scraper]
      |
      v
[n8n Orchestrator] ---> trigger actor run ---> wait ---> collect results
      |
      v
[Python FastAPI Processor]
      |
      +--> Parse & normalize price data
      +--> Compare against historical prices
      +--> Detect drops, increases, stock changes
      +--> Generate alerts
      |
      v
[Airtable Storage]
      |
      +--> Products table (current state)
      +--> PriceHistory table (all observations)
      +--> Alerts table (triggered alerts)
      |
      v
[Notifications]
      +--> Slack channel alerts
      +--> Email notifications for significant changes
```

## Tools & Technologies

| Tool | Purpose |
|------|---------|
| Apify | Web scraping for competitor prices |
| Python 3.11 | Price analysis processor |
| FastAPI | REST API for analysis and webhook ingestion |
| Airtable | Product and price history storage |
| n8n | Workflow orchestration (daily cron) |
| Email (SMTP) | Alert delivery for significant price changes |
| Slack | Real-time alert notifications |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/analyze` | Trigger full price analysis for all products |
| `GET` | `/products` | List all tracked products (filter by competitor) |
| `GET` | `/products/{id}/history` | Price history and stats for a product |
| `GET` | `/alerts` | Recent unacknowledged price alerts |
| `POST` | `/webhook/apify` | Receive scraped price data from Apify |

## Setup

### Apify Scraper

```bash
cd scraper

# Install dependencies
pip install -r requirements.txt

# Deploy to Apify (or run locally)
apify push
```

Configure the scraper actor with your target product URLs in the Apify console.

### Python Processor

```bash
cd processor

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env with your API keys and SMTP credentials

# Start the processor API
uvicorn src.main:app --reload --port 8000
```

### n8n Workflow

Import `workflows/price-monitor.json` into your n8n instance. Update:

1. Apify credentials (API token and actor ID)
2. Slack credentials for alert notifications
3. SMTP credentials for email alerts
4. PriceRadar API URL if not running on localhost

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `APIFY_API_TOKEN` | Apify API authentication token | `apify_api_...` |
| `APIFY_ACTOR_ID` | ID of the price scraper actor | `your-actor-id` |
| `OPENAI_API_KEY` | OpenAI key for analysis summaries | `sk-...` |
| `AIRTABLE_API_KEY` | Airtable personal access token | `pat...` |
| `AIRTABLE_BASE_ID` | Airtable base identifier | `appXXXXXX` |
| `AIRTABLE_PRODUCTS_TABLE` | Products table name | `Products` |
| `AIRTABLE_PRICES_TABLE` | Price history table name | `PriceHistory` |
| `ALERT_EMAIL` | Recipient for price alert emails | `alerts@company.com` |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USER` | SMTP username | `you@gmail.com` |
| `SMTP_PASSWORD` | SMTP password or app password | `xxxx-xxxx-xxxx` |
| `PRICE_CHANGE_THRESHOLD` | Minimum % change to trigger alerts | `5.0` |
