# FormBridge - Universal Webhook-to-CRM Connector

Automatically routes form submissions from any provider to HubSpot CRM and Airtable with real-time Slack notifications. A single API endpoint handles webhooks from Typeform, JotForm, Google Forms, Gravity Forms, or any custom JSON source.

## Supported Form Providers

| Provider | Detection Method | Status |
|----------|-----------------|--------|
| Typeform | `form_response` key in payload | Supported |
| JotForm | `formID` or `rawRequest` key | Supported |
| Google Forms | `response.answers` structure | Supported |
| Gravity Forms | `form` + `entry` keys | Supported |
| Custom JSON | Fallback for any flat/nested JSON | Supported |

## Architecture

```
Form Submission (Typeform / JotForm / Google Forms / Gravity Forms / Custom)
      |
      v
[POST /webhook/{source}]  or  [POST /webhook]  (auto-detect)
      |
      v
[Parser] --> detect source --> extract & normalize fields
      |
      v
[Mapper] --> map normalized fields to CRM schema
      |              |
      v              v
[HubSpot CRM]    [Airtable]
  upsert           log submission
  contact          upsert contact
      |
      v
[Slack Notifier] --> formatted Block Kit message
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/webhook/{source}` | Receive webhook with explicit source (typeform, jotform, etc.) |
| `POST` | `/webhook` | Receive webhook with auto-detected source |
| `GET` | `/submissions` | List all processed submissions from Airtable |
| `GET` | `/submissions/{id}` | Get details of a specific submission |
| `GET` | `/health` | Service health check with dependency status |

## Setup

### Prerequisites

- Python 3.11+
- HubSpot private app access token
- Airtable personal access token and base with `Submissions` and `Contacts` tables
- Slack incoming webhook URL (optional)

### Installation

```bash
# Clone and enter the project directory
cd 06-form-bridge

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start the server
uvicorn src.main:app --reload --port 8000
```

### Docker

```bash
docker build -t form-bridge .
docker run -p 8000:8000 --env-file .env form-bridge
```

### Running Tests

```bash
pytest tests/ -v
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `HUBSPOT_API_KEY` | HubSpot private app access token | `pat-...` |
| `HUBSPOT_PORTAL_ID` | HubSpot portal/account ID | `12345678` |
| `AIRTABLE_API_KEY` | Airtable personal access token | `pat...` |
| `AIRTABLE_BASE_ID` | Airtable base identifier | `appXXXXXX` |
| `AIRTABLE_TABLE_NAME` | Submissions table name | `Submissions` |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL | `https://hooks.slack.com/...` |
| `SLACK_CHANNEL` | Target Slack channel | `#form-submissions` |
| `WEBHOOK_SECRET` | Shared secret for webhook verification | `your-secret` |
| `CORS_ORIGINS` | Allowed CORS origins (JSON array) | `["http://localhost:3000"]` |
| `LOG_LEVEL` | Python logging level | `INFO` |

## Usage Examples

### Typeform Webhook

Configure your Typeform to send webhooks to:
```
POST https://your-domain.com/webhook/typeform
```

### Auto-detect Source

Send any form payload and let FormBridge detect the source:
```
POST https://your-domain.com/webhook
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "company": "Acme Inc"
}
```
