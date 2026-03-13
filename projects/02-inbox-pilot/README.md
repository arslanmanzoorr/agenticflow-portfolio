# Inbox Pilot

AI-powered email classification and auto-response service that integrates with Gmail to automatically categorize incoming emails, analyze sentiment, and generate intelligent draft responses.

## Architecture

```
Gmail Inbox --> Google Pub/Sub --> Inbox Pilot API --> OpenAI (Classification)
                                       |                    |
                                       +-----> Gmail Drafts (Auto-responses)
                                       +-----> Airtable (Logging)
                                       +-----> Slack (Escalation alerts)
```

## Features

- Real-time email classification via Gmail push notifications
- AI-powered categorization: billing, technical, sales, spam, general
- Sentiment analysis: positive, neutral, negative
- Automatic draft response generation with category-specific templates
- Smart escalation rules for urgent or negative emails
- Classification statistics dashboard

## Prerequisites

- Python 3.11+
- OpenAI API key
- Gmail API credentials (OAuth2)
- Airtable account (optional, for logging)

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd 02-inbox-pilot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Start the server

```bash
uvicorn src.main:app --reload --port 8000
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Detailed health check |
| POST | `/webhook/gmail` | Receive Gmail push notification |
| POST | `/webhook/gmail/test` | Test classification with direct payload |
| GET | `/stats` | Get classification statistics |
| GET | `/stats/recent` | Get recent classifications |

### Test Classification

```bash
curl -X POST http://localhost:8000/webhook/gmail/test \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "msg_001",
    "sender": "customer@example.com",
    "subject": "Billing issue",
    "body": "I was charged twice for my subscription."
  }'
```

### Response Example

```json
{
  "message_id": "msg_001",
  "category": "billing",
  "sentiment": "negative",
  "confidence": 0.95,
  "summary": "Customer reports duplicate charge on subscription.",
  "auto_respond": false,
  "escalated": true,
  "classified_at": "2024-01-15T10:30:00Z"
}
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for classification | Yes |
| `GMAIL_CREDENTIALS_PATH` | Path to Gmail OAuth2 credentials | Yes |
| `AIRTABLE_API_KEY` | Airtable API key for logging | No |
| `AIRTABLE_BASE_ID` | Airtable base ID | No |
| `APP_ENV` | Environment (development/production) | No |
| `LOG_LEVEL` | Logging level (INFO/DEBUG/WARNING) | No |
| `PORT` | Server port (default: 8000) | No |

## Running with Docker

```bash
# Build the image
docker build -t inbox-pilot .

# Run the container
docker run -p 8000:8000 --env-file .env inbox-pilot
```

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
02-inbox-pilot/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py             # Environment configuration
│   ├── routers/
│   │   ├── webhook.py        # Gmail webhook handler
│   │   └── stats.py          # Classification statistics
│   ├── services/
│   │   ├── classifier.py     # OpenAI email classifier
│   │   ├── responder.py      # AI response generator
│   │   └── gmail_client.py   # Gmail API wrapper
│   └── models/
│       └── email.py          # Pydantic data models
├── tests/
│   ├── test_classifier.py    # Classifier unit tests
│   └── test_webhook.py       # Webhook integration tests
├── Dockerfile
├── requirements.txt
└── architecture.md
```
