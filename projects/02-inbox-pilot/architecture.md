# Inbox Pilot - Architecture

## System Overview

Inbox Pilot is an AI-powered email classification and auto-response system that
integrates with Gmail via push notifications, classifies incoming emails using
OpenAI, and either auto-responds or escalates based on content analysis.

## Architecture Diagram

```
+------------------+        +-------------------+        +----------------+
|   Gmail Inbox    |------->|  Google Pub/Sub   |------->|  Inbox Pilot   |
|                  |  push  |                   |  POST  |  FastAPI App   |
+------------------+        +-------------------+        +-------+--------+
                                                                 |
                                          +----------------------+----+
                                          |                           |
                                   +------v------+           +-------v-------+
                                   |  Classifier  |           |   Responder   |
                                   |  (OpenAI)    |           |   (OpenAI)    |
                                   +------+-------+           +-------+-------+
                                          |                           |
                                   +------v-------+          +-------v-------+
                                   |   Airtable   |          |  Gmail Drafts |
                                   |   (Logging)  |          |  (Responses)  |
                                   +--------------+          +---------------+
```

## Components

### FastAPI Application (src/main.py)
- Entry point with CORS middleware and lifespan management
- Routes requests to webhook and stats routers

### Webhook Router (src/routers/webhook.py)
- Receives Gmail Pub/Sub push notifications at POST /webhook/gmail
- Orchestrates the classification and response pipeline
- Provides a test endpoint for direct email classification

### Stats Router (src/routers/stats.py)
- Exposes classification metrics at GET /stats
- Returns recent classifications at GET /stats/recent
- Aggregates data from in-memory store

### Email Classifier (src/services/classifier.py)
- Sends email content to OpenAI GPT for classification
- Returns structured results with category, sentiment, and confidence
- Uses JSON mode for reliable parsing

### Email Responder (src/services/responder.py)
- Generates personalized email responses based on classification
- Uses category-specific prompt templates for appropriate tone
- Adjusts tone based on detected sentiment

### Gmail Client (src/services/gmail_client.py)
- Handles Gmail API authentication and operations
- Fetches email content from push notification data
- Creates draft responses in the user's Gmail

## Data Flow

1. New email arrives in Gmail
2. Gmail Pub/Sub sends push notification to /webhook/gmail
3. App fetches full email content via Gmail API
4. Email is classified by OpenAI (category, sentiment, confidence)
5. Based on rules, the email is either:
   - Auto-responded: draft is created in Gmail
   - Escalated: flagged for human review
6. Classification is logged to Airtable and stored in memory for stats

## Decision Logic

- Auto-respond: billing/general category, confidence >= 0.8, non-negative sentiment
- Escalate: negative sentiment, technical category, or confidence < 0.6
