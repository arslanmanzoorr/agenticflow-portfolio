# HireFlow - Recruitment Pipeline Automator

End-to-end recruitment automation system that scrapes candidate profiles from LinkedIn using Apify, scores them with OpenAI, manages the hiring pipeline in Airtable, schedules interviews via Calendly, and sends personalized outreach emails -- all orchestrated through n8n workflows with real-time Slack notifications.

## Tools & Technologies

- **n8n** - Workflow automation and orchestration
- **Apify** - Web scraping platform for LinkedIn candidate sourcing
- **OpenAI (GPT-4)** - AI-powered candidate evaluation and scoring
- **Airtable** - Recruitment pipeline database and CRM
- **Calendly** - Automated interview scheduling
- **Slack** - Real-time hiring notifications and weekly dashboards
- **Email (SMTP)** - Personalized candidate outreach and follow-ups

## Architecture

```
+------------------+     +-------------------+     +------------------+
|   Apify Actor    |     |   n8n Workflows   |     |    Airtable      |
|  LinkedIn Scrape +---->+ Candidate Sourcing+---->+  Candidates      |
|  (Python)        |     |                   |     |  JobOpenings     |
+------------------+     +--------+----------+     |  Pipeline        |
                                  |                +--------+---------+
                         +--------v----------+              |
                         |  OpenAI GPT-4     |              |
                         |  Candidate Eval   |              |
                         |  Score 1-10       |              |
                         +--------+----------+              |
                                  |                         |
                         +--------v----------+     +--------v---------+
                         |  Score >= 7?       |     |   Calendly       |
                         |  IF Node           +---->+   Scheduling     |
                         +--------+----------+     +--------+---------+
                                  |                         |
                         +--------v----------+     +--------v---------+
                         | Email Outreach    |     |   Slack Alerts    |
                         | w/ Calendly Link  |     |   Weekly Report   |
                         +-------------------+     +------------------+
```

## Included Workflows

### 1. Candidate Sourcing (`workflows/candidate-sourcing.json`)
Triggers an Apify actor to scrape LinkedIn profiles matching specified search criteria, parses the results, deduplicates against existing records, and creates new candidate entries in the Airtable Candidates table. Sends a Slack notification with the number of new candidates found.

### 2. Candidate Screening (`workflows/candidate-screening.json`)
Receives new candidate data via webhook, sends the candidate profile and job requirements to OpenAI GPT-4 for evaluation, and updates the Airtable record with an AI score (1-10) and detailed assessment. Candidates scoring 7 or above automatically receive a personalized outreach email with a Calendly interview booking link. Lower-scoring candidates are logged in Slack for awareness.

### 3. Pipeline Tracker (`workflows/pipeline-tracker.json`)
Runs every Monday at 9am to generate a weekly hiring dashboard. Reads all pipeline records from Airtable, aggregates statistics (candidates per stage, average days in stage), and posts a formatted Slack block message. Identifies candidates stuck in a stage for more than 7 days and sends follow-up reminder emails to the hiring manager.

## Airtable Schema

The system uses three interconnected tables:

### Candidates
Stores all sourced candidate information including contact details, skills, experience, AI evaluation scores, and current recruitment status. Linked to Pipeline records.

### JobOpenings
Manages active job requisitions with required skills, minimum experience, descriptions, and status tracking. Linked to Pipeline records to see all candidates for each role.

### Pipeline
Junction table connecting Candidates to JobOpenings, tracking the interview stage, Calendly links, interview dates, feedback, and ratings. Serves as the core workflow tracker.

See `schemas/airtable-base.json` for the complete field definitions and types.

## Email Templates

Two HTML email templates are included in the `templates/` directory:

- **outreach-email.html** - Personalized candidate outreach with Calendly scheduling link
- **rejection-email.html** - Professional rejection notice with encouragement

Both templates use placeholder variables (`{{candidate_name}}`, `{{job_title}}`, `{{company_name}}`, `{{calendly_link}}`, `{{recruiter_name}}`) that are populated by the n8n workflows at send time.

## Setup

1. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and credentials
   ```

2. **Set up Apify actor**
   - Deploy the LinkedIn scraper from `apify/linkedin-scraper.py` to your Apify account
   - Configure the actor input in `apify/apify.json`
   - Add your Apify API token to `.env`

3. **Create the Airtable base**
   - Use `schemas/airtable-base.json` as a reference to create the three tables
   - Configure field types and linked record relationships
   - Add your Airtable API key and base ID to `.env`

4. **Configure Calendly**
   - Create an event type for interviews
   - Add the Calendly API key and event type URL to `.env`

5. **Set up email (SMTP)**
   - Configure Gmail app password or your SMTP provider
   - Add SMTP credentials to `.env`

6. **Import n8n workflows**
   - Import all JSON files from `workflows/` into your n8n instance
   - Set environment variables in n8n matching your `.env` file
   - Configure credential nodes (Airtable, SMTP, HTTP Header Auth for OpenAI and Calendly)

7. **Activate workflows**
   - Enable the Candidate Sourcing workflow on your desired schedule
   - Enable the Pipeline Tracker for weekly Monday reports
   - The Candidate Screening workflow activates automatically via webhook

## Slack Notifications

The system sends notifications to the configured Slack channel for:

- New candidates sourced from LinkedIn
- AI screening results (qualified and below-threshold)
- Weekly pipeline dashboard with stage breakdowns
- Stale candidate alerts when follow-up is needed
