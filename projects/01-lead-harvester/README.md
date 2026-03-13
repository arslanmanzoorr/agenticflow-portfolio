# Lead Harvester - Automated Lead Generation & Enrichment Pipeline

An n8n-powered automation system that scrapes business leads from Google Maps via Apify, enriches them with Clearbit data, scores them based on configurable criteria, and routes qualified leads to HubSpot CRM while logging everything to Airtable.

## Architecture

```
+------------------+     +------------------+     +------------------+
|   Cron Trigger   |---->|  Apify Scraper   |---->|   Wait for Run   |
|  (Daily 9:00AM)  |     |  (Google Maps)   |     |   (30 seconds)   |
+------------------+     +------------------+     +------------------+
                                                          |
                                                          v
+------------------+     +------------------+     +------------------+
|  Lead Scoring    |<----|    Clearbit       |<----|  Fetch Results   |
|  (Function Node) |     |   Enrichment     |     |  & Clean Data    |
+------------------+     +------------------+     +------------------+
        |
        v
+------------------+
|   IF Qualified   |
|  (score >= 70)   |
+-------+----------+
        |
   +----+----+
   |         |
   v         v
+------+  +--------+     +------------------+
|HubSpot| |Airtable|---->| Slack Summary    |
|Create |  | Log    |     | Notification     |
|Contact|  | Lead   |     +------------------+
+------+  +--------+

Daily Summary Workflow:
+------------------+     +------------------+     +------------------+
|   Cron Trigger   |---->| Airtable: Get    |---->| Format & Send    |
|  (Daily 6:00PM)  |     | Today's Leads    |     | Slack Summary    |
+------------------+     +------------------+     +------------------+
```

## Prerequisites

- [n8n](https://n8n.io/) (self-hosted or cloud) v1.0+
- [Apify](https://apify.com/) account with Google Maps Scraper actor
- [Airtable](https://airtable.com/) account with base set up per schema
- [HubSpot](https://www.hubspot.com/) account (free CRM tier works)
- [Clearbit](https://clearbit.com/) API access
- [Slack](https://slack.com/) workspace with incoming webhook configured

## Setup Instructions

### 1. Clone & Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual API keys and tokens
```

### 2. Set Up Airtable Base

Create an Airtable base with the structure defined in `schemas/airtable-base.json`:

- **Leads** table: name, email, phone, company, website, source, score, status, enrichment_data, created_at
- **ScoringLog** table: lead_id, score, factors, timestamp

### 3. Configure Apify Actor

1. Go to [Apify Console](https://console.apify.com/)
2. Find the "Google Maps Scraper" actor
3. Use the configuration in `apify/actor-config.json` as a starting point
4. Note your actor task ID for the workflow

### 4. Import n8n Workflows

1. Open your n8n instance
2. Go to **Workflows** > **Import from File**
3. Import `workflows/lead-harvester-main.json`
4. Import `workflows/daily-summary.json`
5. Update credential references in each workflow to match your n8n credentials

### 5. Configure n8n Credentials

In n8n, create the following credentials:
- **Header Auth** for Apify API (token as Bearer)
- **Header Auth** for Clearbit API
- **Header Auth** for HubSpot API
- **Header Auth** for Airtable API

### 6. Activate Workflows

Enable both workflows in n8n to start automated lead harvesting.

## Workflow Descriptions

### lead-harvester-main.json
The primary workflow that runs daily at 9:00 AM. It triggers an Apify Google Maps scraping run, waits for completion, fetches and cleans the results, enriches leads via Clearbit, applies a scoring algorithm, and routes qualified leads (score >= 70) to HubSpot while logging all leads to Airtable. A Slack notification is sent with a summary of the run.

### daily-summary.json
A lightweight workflow that runs daily at 6:00 PM. It queries Airtable for all leads created that day, formats a summary report, and posts it to Slack for team visibility.

## Environment Variables

| Variable | Description |
|---|---|
| `APIFY_API_TOKEN` | Your Apify API token for authentication |
| `AIRTABLE_API_KEY` | Airtable personal access token |
| `AIRTABLE_BASE_ID` | The ID of your Airtable base (starts with `app`) |
| `HUBSPOT_API_KEY` | HubSpot private app access token |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL for notifications |
| `CLEARBIT_API_KEY` | Clearbit API key for lead enrichment |

## Lead Scoring Logic

The scoring function assigns points based on:

| Factor | Points | Condition |
|---|---|---|
| Has email | +20 | Email field is not empty |
| Has website | +15 | Website URL is present |
| Has phone | +10 | Phone number is present |
| Company size | +10 to +30 | Based on Clearbit employee count |
| Industry match | +20 | Company industry matches target list |
| Location match | +10 | Company is in target geography |

Leads scoring **70 or above** are considered qualified and are pushed to HubSpot.

## How to Import into n8n

1. Open your n8n editor
2. Click the **three-dot menu** (top right) or go to **Workflows**
3. Select **Import from File**
4. Choose the `.json` workflow file
5. Review the imported nodes and update any credential references
6. Set your environment variables or hardcode values in the HTTP Request nodes
7. Click **Save** and then **Activate** the workflow

## Customization

- Adjust search terms and locations in `apify/actor-config.json`
- Modify scoring weights in the Function node within the main workflow
- Change the qualification threshold in the IF node (default: 70)
- Add additional enrichment sources by inserting HTTP Request nodes before scoring

## License

MIT
