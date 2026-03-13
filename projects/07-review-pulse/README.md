# ReviewPulse - Review Aggregator & Sentiment Analyzer

Automated system that scrapes customer reviews from multiple platforms, runs AI-powered sentiment analysis, stores structured data in Airtable, and sends real-time Slack alerts for negative reviews.

## Tools & Technologies

- **Apify** - Web scraping actors for Google Maps, Yelp, and Trustpilot reviews
- **Python / FastAPI** - REST API for review ingestion, analysis, and dashboard
- **OpenAI GPT-4o** - Sentiment analysis, category scoring, and periodic summaries
- **Airtable** - Structured storage for reviews, sentiment results, and summaries
- **n8n** - Workflow orchestration (daily scraping, weekly summaries)
- **Slack** - Real-time webhook alerts for negative reviews
- **Docker** - Containerized deployment

## Architecture

```
Apify Scrapers ──> n8n Orchestration ──> FastAPI API ──> OpenAI Sentiment
                                              │
                                              ├──> Airtable (Reviews + Summaries)
                                              └──> Slack Alerts (Negative Reviews)
```

**Daily flow:** n8n triggers Apify actors at 6 AM, collects results, posts them to the FastAPI webhook, runs sentiment analysis, and alerts on negative reviews.

**Weekly flow:** Every Monday at 9 AM, n8n calls the `/summarize` endpoint to generate a GPT-powered weekly review summary and posts it to Slack.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/webhook/reviews` | Receive scraped reviews from Apify/n8n |
| `POST` | `/analyze` | Run sentiment analysis on a batch of reviews |
| `GET` | `/reviews` | List reviews (filters: `source`, `rating`, `sentiment`) |
| `GET` | `/reviews/{id}` | Get a single review by ID |
| `GET` | `/dashboard` | Aggregate stats: avg rating, sentiment breakdown, review count by source |
| `POST` | `/summarize` | Generate AI summary of recent reviews (query param: `period_days`) |
| `GET` | `/summaries` | List previously generated summaries |

### Query Parameters

**GET /reviews**
- `source` - Filter by platform (`google_maps`, `yelp`, `trustpilot`)
- `rating` - Filter by star rating (0-5)
- `sentiment` - Filter by sentiment label (`positive`, `neutral`, `negative`)
- `limit` - Max results (default: 100, max: 500)

**POST /summarize**
- `period_days` - Look-back window in days (default: 7, max: 90)

## Setup

### Prerequisites

- Python 3.11+
- Apify account with a review scraping actor
- OpenAI API key
- Airtable base with `Reviews` and `SentimentAnalysis` tables
- Slack incoming webhook URL
- n8n instance (self-hosted or cloud)

### Environment Variables

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

### Local Development

```bash
cd api
pip install -r requirements.txt
uvicorn api.src.main:app --reload --port 8000
```

### Docker

```bash
docker build -t review-pulse .
docker run -p 8000:8000 --env-file .env review-pulse
```

### Airtable Setup

Create a base with the following tables:

**Reviews** - `ReviewID`, `Platform`, `BusinessID`, `BusinessName`, `ReviewerName`, `Rating`, `Text`, `Date`, `ScrapedAt`, `Language`

**SentimentAnalysis** - `ReviewID`, `OverallScore`, `Label`, `Confidence`, `KeyPhrases`, `Summary`, `ModelUsed`, `AnalyzedAt`

### n8n Workflow

Import `workflows/review-collector.json` into your n8n instance and configure:

1. Set the Apify API token credential
2. Set environment variables: `APIFY_ACTOR_ID`, `REVIEW_URLS`, `API_BASE_URL`, `SLACK_WEBHOOK_URL`
3. Activate the workflow

## Project Structure

```
07-review-pulse/
├── apify/                    # Apify scraper actor
│   ├── main.py
│   ├── apify.json
│   └── requirements.txt
├── api/
│   ├── requirements.txt
│   └── src/
│       ├── __init__.py
│       ├── config.py          # Pydantic settings
│       ├── main.py            # FastAPI application
│       ├── models/
│       │   ├── __init__.py
│       │   └── review.py      # Pydantic models
│       └── services/
│           ├── __init__.py
│           ├── sentiment.py        # OpenAI sentiment analyzer
│           ├── airtable_client.py  # Airtable CRUD
│           └── alert_service.py    # Slack alert dispatcher
├── workflows/
│   └── review-collector.json  # n8n workflow
├── .env.example
├── Dockerfile
└── README.md
```
