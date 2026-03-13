# Arslan Manzoor - AI & Automation Portfolio

A comprehensive portfolio showcasing real-world automation projects built with n8n, Python, Apify, Airtable, HubSpot, OpenAI, and more.

## Portfolio Website

Built with **Next.js 14**, **Tailwind CSS**, and **Framer Motion**. Dark theme with smooth animations, project showcases, and contact form.

```bash
cd portfolio-site
npm install
npm run dev
```

Visit `http://localhost:3000`

## Projects

| # | Project | Description | Tech Stack |
|---|---------|-------------|------------|
| 01 | **LeadHarvester** | Automated lead generation pipeline | n8n, Apify, Airtable, HubSpot |
| 02 | **InboxPilot** | AI email classifier & auto-responder | Python, FastAPI, OpenAI, Gmail API, Airtable |
| 03 | **ShopSync** | E-commerce order & inventory automation | n8n, Shopify, Airtable, Slack |
| 04 | **ContentEngine** | AI social media content pipeline | Python, FastAPI, OpenAI, Airtable, n8n |
| 05 | **PriceRadar** | Competitor price monitoring system | Apify, Python, Airtable, n8n, Email |
| 06 | **FormBridge** | Universal webhook-to-CRM connector | Python, FastAPI, Webhooks, HubSpot, Airtable |
| 07 | **ReviewPulse** | Review aggregator & sentiment analyzer | Apify, Python, OpenAI, Airtable, n8n |
| 08 | **MeetingMind** | AI meeting notes automation | Python, FastAPI, Whisper, GPT-4, Airtable, Slack |
| 09 | **DataSync Pro** | Multi-database sync engine | n8n, Airtable, Google Sheets, PostgreSQL |
| 10 | **HireFlow** | Recruitment pipeline automator | n8n, Apify, OpenAI, Airtable, Calendly |

## Project Structure

```
arslan-portfolio/
  portfolio-site/          # Next.js portfolio website
    src/
      app/                 # Pages (Home, Projects, About, Contact)
      components/          # React components
      data/                # Project data files
      types/               # TypeScript interfaces
  projects/
    01-lead-harvester/     # n8n workflows + Apify scraper
    02-inbox-pilot/        # Python FastAPI email automation
    03-shop-sync/          # n8n e-commerce workflows
    04-content-engine/     # Python API + n8n scheduler
    05-price-radar/        # Apify + Python + n8n monitoring
    06-form-bridge/        # Python webhook-to-CRM bridge
    07-review-pulse/       # Full-stack review system
    08-meeting-mind/       # Python Whisper + GPT API
    09-data-sync-pro/      # n8n multi-DB sync
    10-hire-flow/          # n8n + Apify recruitment
```

## Getting Started

### Portfolio Website
```bash
cd portfolio-site
npm install
npm run dev
```

### Python Projects (02, 04, 05, 06, 07, 08)
```bash
cd projects/<project-name>
cp .env.example .env
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### n8n Workflows (01, 03, 09, 10)
1. Import workflow JSON files into your n8n instance
2. Configure credentials for Airtable, Slack, etc.
3. Activate the workflows

## Tools & Technologies

- **Automation**: n8n, Make.com, Zapier
- **Programming**: Python, FastAPI, TypeScript, Next.js
- **AI/ML**: OpenAI GPT-4, Whisper, Sentiment Analysis
- **Databases**: Airtable, PostgreSQL, Google Sheets
- **Scraping**: Apify
- **CRM**: HubSpot
- **Communication**: Slack, Email (SMTP)
- **Scheduling**: Calendly
- **Frontend**: React, Tailwind CSS, Framer Motion

## Contact

- Website: [arslanmanzoor.site](https://arslanmanzoor.site)
"# agenticflow-portfolio" 
