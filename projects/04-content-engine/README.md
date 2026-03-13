# ContentEngine - AI Social Media Content Pipeline

Hybrid Python FastAPI + n8n workflow that generates platform-optimized social media content using OpenAI, stores results in Airtable, and automates publishing schedules via n8n.

## Architecture

```
User Request
    |
    v
[FastAPI API] --> [OpenAI GPT-4] --> generate platform-optimized content
    |                                        |
    v                                        v
[Airtable]  <----  store content record  <----
    |
    v
[n8n Scheduler] --> poll for scheduled content --> publish via platform APIs
    |
    v
[Slack Notification] --> notify on publish success/failure
```

**Flow summary:** A client sends a topic and target platform to the FastAPI service. The service calls OpenAI GPT-4 to produce a post tailored for that platform (character limits, hashtags, tone), generates a companion DALL-E image prompt, and persists everything to Airtable. An n8n cron workflow periodically checks Airtable for content whose scheduled publish time has arrived, pushes it to the platform API, and sends a Slack notification on completion.

## Tools & Technologies

| Tool | Purpose |
|------|---------|
| Python 3.11 | Core runtime |
| FastAPI | REST API framework |
| OpenAI GPT-4 | Content generation |
| Airtable | Content storage & calendar |
| n8n | Workflow orchestration & scheduling |
| Docker | Container deployment |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/generate` | Generate content for a single platform |
| `POST` | `/batch` | Generate content for multiple platforms at once |
| `GET` | `/content/{id}` | Retrieve a generated content piece by ID |
| `POST` | `/schedule` | Schedule content for future publishing |
| `GET` | `/analytics` | Aggregate content performance statistics |
| `GET` | `/health` | Service health check |

## Setup

### Prerequisites

- Python 3.11+
- OpenAI API key
- Airtable account with a base containing `Generated Content` and `Content Calendar` tables
- n8n instance (self-hosted or cloud) for scheduling workflows

### Installation

```bash
# Clone and enter the project directory
cd 04-content-engine

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start the API server
uvicorn api.src.main:app --reload --port 8000
```

### Docker

```bash
docker build -t content-engine .
docker run -p 8000:8000 --env-file .env content-engine
```

### n8n Workflow

Import `workflows/content-scheduler.json` into your n8n instance. Update the Airtable and Slack credentials in the workflow settings.

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `OPENAI_MODEL` | Chat completion model | `gpt-4` |
| `AIRTABLE_API_KEY` | Airtable personal access token | `pat...` |
| `AIRTABLE_BASE_ID` | Airtable base identifier | `appXXXXXX` |
| `AIRTABLE_TABLE_NAME` | Primary content table name | `Content` |
| `CORS_ORIGINS` | Allowed CORS origins (JSON array) | `["http://localhost:3000"]` |
| `APP_NAME` | Application display name | `ContentEngine` |
| `APP_VERSION` | Semantic version | `1.0.0` |
| `N8N_WEBHOOK_URL` | n8n webhook trigger endpoint | `http://localhost:5678/webhook/content-engine` |
