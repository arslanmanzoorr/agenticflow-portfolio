import { Project } from "@/types";

export const projects: Project[] = [
  {
    id: 1,
    slug: "lead-harvester",
    title: "LeadHarvester",
    tagline:
      "Automated lead generation pipeline that scrapes, enriches, scores, and delivers qualified prospects directly to your CRM.",
    description:
      "LeadHarvester eliminates the grind of manual prospecting by combining web scraping with intelligent lead scoring. It pulls business data from online directories, enriches contacts through third-party APIs, and uses an AI-driven algorithm to rank prospects before pushing them straight into HubSpot.",
    problem:
      "Businesses spend hours manually finding and qualifying leads from scattered online sources, resulting in slow pipelines and missed opportunities.",
    solution:
      "An automated pipeline using Apify to scrape business directories, n8n to orchestrate enrichment and scoring workflows, HubSpot for CRM management, and Airtable for centralized logging.",
    tools: ["n8n", "Apify", "Airtable", "HubSpot"],
    category: "Lead Generation",
    type: "n8n",
    featured: true,
    features: [
      "Automated web scraping from business directories",
      "Lead enrichment with contact data APIs",
      "AI-powered lead scoring",
      "CRM auto-population",
      "Daily Slack summary reports",
      "Configurable scraping criteria",
    ],
    architecture: [
      "Scheduled trigger initiates Apify scrape",
      "n8n processes and cleans raw data",
      "Enrichment APIs add contact details",
      "Scoring algorithm qualifies leads",
      "Qualified leads pushed to HubSpot",
      "All data logged to Airtable",
      "Daily summary sent to Slack",
    ],
  },
  {
    id: 2,
    slug: "inbox-pilot",
    title: "InboxPilot",
    tagline:
      "AI-powered email triage system that classifies, analyzes sentiment, and auto-drafts responses so your support team can focus on what matters.",
    description:
      "InboxPilot hooks into Gmail via push notifications and runs every incoming message through OpenAI for classification and sentiment analysis. Routine inquiries get auto-drafted replies while complex or negative emails are escalated to the right human agent instantly.",
    problem:
      "Support teams waste valuable time triaging repetitive emails, leading to slow response times and agent burnout.",
    solution:
      "A FastAPI webhook receives Gmail notifications in real time, OpenAI classifies each email by category and sentiment, and the system either auto-drafts a response or escalates to the appropriate team member.",
    tools: ["Python", "FastAPI", "OpenAI", "Gmail API", "Airtable"],
    category: "AI/ML",
    type: "python",
    featured: true,
    features: [
      "Real-time email classification (billing, technical, sales, spam)",
      "Sentiment analysis on incoming emails",
      "AI-powered auto-response drafting",
      "Smart escalation to human agents",
      "Classification analytics dashboard",
      "Template-based personalized responses",
    ],
    architecture: [
      "Gmail push notification triggers webhook",
      "FastAPI processes email content",
      "OpenAI classifies category and sentiment",
      "Router determines auto-respond or escalate",
      "Auto-responses drafted with LLM",
      "Escalations logged to Airtable",
      "Stats API serves dashboard data",
    ],
  },
  {
    id: 3,
    slug: "shop-sync",
    title: "ShopSync",
    tagline:
      "Real-time Shopify order and inventory sync that keeps your stock accurate and your team informed.",
    description:
      "ShopSync listens for Shopify webhooks to process orders the moment they arrive. Inventory levels are tracked in Airtable, low-stock alerts fire to Slack and email, and a daily summary keeps stakeholders in the loop without lifting a finger.",
    problem:
      "Online sellers manually sync orders and inventory across platforms, leading to overselling, stockouts, and wasted hours on data entry.",
    solution:
      "Shopify webhooks trigger n8n workflows that manage inventory in Airtable, send automated restock alerts via Slack and email, and generate daily order summary reports.",
    tools: ["n8n", "Shopify", "Airtable", "Slack", "SMTP"],
    category: "E-commerce",
    type: "n8n",
    features: [
      "Real-time order processing via webhooks",
      "Automated inventory tracking",
      "Low-stock alerts to Slack and email",
      "Supplier restock notifications",
      "Daily order summary reports",
      "Multi-store support",
    ],
    architecture: [
      "Shopify webhook fires on new order",
      "n8n receives and validates order data",
      "Inventory checked and decremented in Airtable",
      "Low stock triggers Slack + email alerts",
      "Order logged with fulfillment status",
      "Scheduled daily summary report",
    ],
  },
  {
    id: 4,
    slug: "content-engine",
    title: "ContentEngine",
    tagline:
      "AI content factory that generates, schedules, and publishes multi-platform social media posts from a single brief.",
    description:
      "ContentEngine turns a short topic brief into platform-optimized posts for Twitter, LinkedIn, and Instagram. Generated content lands in an Airtable calendar for approval, and n8n handles scheduled publishing to each platform automatically.",
    problem:
      "Maintaining a consistent social media presence requires hours of content creation, reformatting for each platform, and manual scheduling.",
    solution:
      "A Python API generates multi-platform content variants with OpenAI, stores them in an Airtable content calendar, and n8n publishes approved posts on a configurable schedule.",
    tools: ["Python", "FastAPI", "OpenAI", "Airtable", "n8n"],
    category: "AI/ML",
    type: "hybrid",
    featured: true,
    features: [
      "Multi-platform content generation (Twitter, LinkedIn, Instagram)",
      "AI-powered content variants from single brief",
      "Airtable content calendar management",
      "Scheduled automated publishing",
      "Engagement metrics tracking",
      "Tone and style customization",
    ],
    architecture: [
      "User submits topic via API",
      "FastAPI + OpenAI generates post variants",
      "Content stored in Airtable as drafts",
      "User approves posts in Airtable",
      "n8n scheduled workflow picks approved posts",
      "Posts published to social platforms",
      "Engagement data pulled back",
    ],
  },
  {
    id: 5,
    slug: "price-radar",
    title: "PriceRadar",
    tagline:
      "Competitor price intelligence system that scrapes, compares, and alerts you to market shifts before they impact your margins.",
    description:
      "PriceRadar continuously monitors competitor pricing using Apify scrapers, normalizes the data through a Python engine, and sends threshold-based alerts when significant changes occur. Weekly trend reports help you stay ahead of market movements.",
    problem:
      "E-commerce businesses need to track competitor pricing to stay competitive, but manual tracking across dozens of products and competitors is unsustainable.",
    solution:
      "Apify scrapes competitor prices on a schedule, Python normalizes and compares the data against your own pricing, and n8n orchestrates the pipeline while sending alert emails on significant changes.",
    tools: ["Apify", "Python", "Airtable", "n8n", "SMTP"],
    category: "E-commerce",
    type: "hybrid",
    features: [
      "Automated competitor price scraping",
      "Price normalization and comparison engine",
      "Configurable price change thresholds",
      "Historical price tracking",
      "Automated alert emails on significant changes",
      "Weekly trend analysis reports",
    ],
    architecture: [
      "Scheduled trigger activates Apify scraper",
      "Raw price data collected from competitors",
      "Python normalizes and compares against your prices",
      "Price history updated in Airtable",
      "Significant changes trigger alert emails",
      "Weekly trend report generated",
    ],
  },
  {
    id: 6,
    slug: "form-bridge",
    title: "FormBridge",
    tagline:
      "Universal form-to-CRM bridge that captures leads from any form tool and funnels them into HubSpot with zero manual work.",
    description:
      "FormBridge acts as a single webhook receiver for every form tool your business uses. Configurable field mappings normalize the data, deduplication prevents duplicate contacts, and every lead is synced to HubSpot with full source attribution.",
    problem:
      "Businesses use multiple form tools across their website, landing pages, and campaigns, but need all leads centralized in one CRM without manual copy-pasting.",
    solution:
      "A generic FastAPI webhook receiver with configurable field mapping per form provider, automatic deduplication by email, and real-time CRM sync to HubSpot.",
    tools: ["Python", "FastAPI", "Webhooks", "HubSpot", "Airtable", "Slack"],
    category: "CRM",
    type: "python",
    features: [
      "Universal webhook receiver for any form tool",
      "Configurable field mapping per provider",
      "Contact deduplication by email",
      "HubSpot CRM auto-population",
      "Source attribution tracking",
      "Real-time Slack notifications",
    ],
    architecture: [
      "Form submission triggers webhook POST",
      "FastAPI normalizes via field mapping config",
      "Deduplication checks existing contacts",
      "New/updated contact synced to HubSpot",
      "Submission logged in Airtable",
      "Slack notification sent to sales channel",
    ],
  },
  {
    id: 7,
    slug: "review-pulse",
    title: "ReviewPulse",
    tagline:
      "Multi-platform review monitoring with AI sentiment analysis that catches negative feedback before it spirals.",
    description:
      "ReviewPulse scrapes customer reviews from multiple platforms daily, runs each through OpenAI for sentiment scoring and theme extraction, and immediately flags negative reviews in Slack so your team can respond fast. A dashboard API powers trend visualization over time.",
    problem:
      "Businesses struggle to monitor customer reviews scattered across Google, Yelp, Trustpilot, and industry-specific platforms, often missing critical negative feedback.",
    solution:
      "Apify scrapes reviews on a schedule, Python processes them through OpenAI for sentiment analysis and theme extraction, negative reviews trigger instant Slack alerts, and n8n orchestrates the entire daily pipeline.",
    tools: [
      "Apify",
      "Python",
      "FastAPI",
      "OpenAI",
      "Airtable",
      "n8n",
      "Slack",
    ],
    category: "AI/ML",
    type: "hybrid",
    featured: true,
    features: [
      "Multi-platform review scraping",
      "AI sentiment analysis with theme extraction",
      "Negative review alerting",
      "Sentiment trend dashboard",
      "Automated daily pipeline",
      "Review response suggestions",
    ],
    architecture: [
      "Scheduled Apify scrapes review platforms",
      "Raw reviews sent to Python processor",
      "OpenAI analyzes sentiment and extracts themes",
      "Results stored in Airtable with scores",
      "Negative reviews trigger Slack alerts",
      "Dashboard API serves trend data",
    ],
  },
  {
    id: 8,
    slug: "meeting-mind",
    title: "MeetingMind",
    tagline:
      "AI meeting assistant that transcribes, summarizes, and distributes action items so nothing falls through the cracks.",
    description:
      "MeetingMind accepts audio uploads through a simple API, transcribes them with Whisper, and uses GPT-4 to generate structured summaries with extracted action items and decision points. Results are archived in Airtable and distributed via Slack and email automatically.",
    problem:
      "Important action items and key decisions get lost after meetings because note-taking is inconsistent and follow-up tracking is manual.",
    solution:
      "An API endpoint accepts audio uploads, Whisper transcribes the recording, GPT-4 summarizes the content and extracts action items with owner assignments, and the results are distributed via Slack and email.",
    tools: [
      "Python",
      "FastAPI",
      "OpenAI Whisper",
      "GPT-4",
      "Airtable",
      "Slack",
    ],
    category: "AI/ML",
    type: "python",
    features: [
      "Audio transcription with Whisper API",
      "AI meeting summarization",
      "Action item extraction with owner assignment",
      "Decision point identification",
      "Automated Slack distribution",
      "Searchable meeting archive",
    ],
    architecture: [
      "Audio file uploaded via API endpoint",
      "Whisper API transcribes to text",
      "GPT summarizes and extracts action items",
      "Structured notes stored in Airtable",
      "Summary posted to Slack channel",
      "Email sent to meeting attendees",
    ],
  },
  {
    id: 9,
    slug: "data-sync-pro",
    title: "DataSync Pro",
    tagline:
      "Bidirectional data sync engine that keeps Airtable, Google Sheets, and PostgreSQL in perfect harmony.",
    description:
      "DataSync Pro monitors changes across multiple data sources using webhooks and polling, applies configurable transformation rules, and handles conflict resolution for true bidirectional synchronization. Built-in retry logic and admin alerts ensure nothing slips through.",
    problem:
      "Companies with data spread across multiple systems face constant inconsistencies, leading to reporting errors and duplicated manual effort to keep everything in sync.",
    solution:
      "n8n workflows monitor changes across Airtable, Google Sheets, and PostgreSQL, apply transformation rules to normalize data, and handle conflict resolution for reliable bidirectional sync.",
    tools: ["n8n", "Airtable", "Google Sheets", "PostgreSQL", "Webhooks"],
    category: "Data",
    type: "n8n",
    features: [
      "Bidirectional data synchronization",
      "Configurable field mapping and transforms",
      "Conflict resolution strategies",
      "Error handling with automatic retry",
      "Multi-source support (Airtable, Sheets, PostgreSQL)",
      "Admin alerts on sync failures",
    ],
    architecture: [
      "Change detection via webhooks and polling",
      "Data transformation engine applies rules",
      "Conflict resolution checks applied",
      "Writes propagated to target systems",
      "Errors caught and retried automatically",
      "Admin notified of persistent failures",
    ],
  },
  {
    id: 10,
    slug: "hire-flow",
    title: "HireFlow",
    tagline:
      "End-to-end recruitment automation that scrapes applications, scores candidates with AI, and books interviews on autopilot.",
    description:
      "HireFlow pulls new applications from job boards via Apify, scores each candidate against the job description using OpenAI, and automatically sends personalized responses with Calendly interview links for top matches. Recruiters get a daily digest of qualified candidates without touching a spreadsheet.",
    problem:
      "Recruiters manually track candidates across job boards, emails, and spreadsheets, creating bottlenecks that slow hiring and let top candidates slip away.",
    solution:
      "Apify scrapes applications from job boards, n8n processes them through OpenAI for candidate scoring against the job description, and auto-sends personalized emails with Calendly links for qualified candidates.",
    tools: ["n8n", "Apify", "OpenAI", "Airtable", "SMTP", "Calendly"],
    category: "HR",
    type: "n8n",
    features: [
      "Automated application scraping from job boards",
      "AI-powered candidate scoring against job description",
      "Automated personalized email responses",
      "Calendly integration for interview scheduling",
      "Candidate tracking in Airtable",
      "Daily qualified candidate digest",
    ],
    architecture: [
      "Apify scrapes new applications",
      "n8n receives and parses resume data",
      "OpenAI scores candidate fit",
      "Airtable updated with score and status",
      "Auto-email sent (rejection or interview invite)",
      "Interview invites include Calendly link",
      "Daily digest sent to hiring manager",
    ],
  },
  {
    id: 11,
    slug: "claw-inbox",
    title: "ClawInbox",
    tagline:
      "OpenClaw-powered email command center that reads, classifies, drafts, and sends your daily briefing before your morning coffee.",
    description:
      "ClawInbox deploys an OpenClaw agent connected to Gmail and Outlook that processes your entire inbox overnight. It classifies emails by urgency and topic, drafts contextual responses for routine messages, flags critical items, and delivers a prioritized morning briefing via Slack or Telegram.",
    problem:
      "Professionals spend 2-3 hours daily managing email — reading, sorting, and drafting responses to repetitive messages while critical items get buried.",
    solution:
      "An OpenClaw agent with Gmail/Outlook channel integration, OpenAI-powered classification and drafting, Airtable logging, and Slack/Telegram briefing delivery — all running on a secure Docker-isolated deployment.",
    tools: ["OpenClaw", "Python", "OpenAI", "Gmail API", "Slack", "Docker"],
    category: "OpenClaw",
    type: "hybrid",
    featured: true,
    features: [
      "Automated email classification by urgency and topic",
      "AI-powered response drafting for routine emails",
      "Morning briefing delivered to Slack or Telegram",
      "Critical email flagging with instant alerts",
      "Docker-isolated secure deployment",
      "Multi-account support (Gmail + Outlook)",
    ],
    architecture: [
      "OpenClaw agent monitors inbox via channel integration",
      "Emails classified by OpenAI (urgency, topic, sentiment)",
      "Routine messages get auto-drafted responses",
      "Critical items flagged for immediate attention",
      "All activity logged to Airtable",
      "Morning briefing compiled and sent to Slack/Telegram",
    ],
  },
  {
    id: 12,
    slug: "claw-support",
    title: "ClawSupport",
    tagline:
      "AI customer support agent built on OpenClaw that resolves tickets from your knowledge base and escalates what it can't handle.",
    description:
      "ClawSupport connects OpenClaw to your helpdesk (Zendesk, Freshdesk, or custom) and uses RAG with your documentation to answer customer questions accurately. It handles L1 support autonomously, escalates complex issues to humans, and learns from resolved tickets to improve over time.",
    problem:
      "Support teams are overwhelmed with repetitive L1 tickets while customers wait hours for answers that already exist in the documentation.",
    solution:
      "An OpenClaw agent with RAG-powered knowledge base search, multi-channel ticket ingestion, autonomous L1 resolution, smart escalation rules, and continuous learning from resolved tickets.",
    tools: ["OpenClaw", "Python", "FastAPI", "OpenAI", "Airtable", "Slack"],
    category: "OpenClaw",
    type: "hybrid",
    features: [
      "RAG-powered answers from your documentation",
      "Multi-channel support (email, Slack, web chat)",
      "Autonomous L1 ticket resolution",
      "Smart escalation to human agents",
      "Resolution metrics dashboard",
      "Continuous learning from resolved tickets",
    ],
    architecture: [
      "Support ticket received via channel integration",
      "OpenClaw queries knowledge base using RAG",
      "High-confidence answers sent automatically",
      "Low-confidence tickets escalated to humans",
      "Resolution logged to Airtable with metrics",
      "Weekly report generated with resolution stats",
    ],
  },
  {
    id: 13,
    slug: "claw-client-manager",
    title: "ClawClientManager",
    tagline:
      "AI client management agent that monitors communications, auto-triages requests, drafts responses, and ensures nothing falls through the cracks.",
    description:
      "ClawClientManager deploys an OpenClaw agent that monitors Slack channels, email, and WhatsApp for client requests. It auto-triages by urgency, drafts contextual responses using conversation history, schedules follow-ups, and sends you a daily client health dashboard.",
    problem:
      "Agencies and consultants juggle multiple client communications across channels, leading to missed messages, slow responses, and dropped follow-ups.",
    solution:
      "An OpenClaw agent with multi-channel monitoring (Slack, email, WhatsApp), AI-powered triage and response drafting, CRM integration for context, and automated follow-up scheduling.",
    tools: ["OpenClaw", "Python", "OpenAI", "HubSpot", "Slack", "WhatsApp API"],
    category: "OpenClaw",
    type: "hybrid",
    features: [
      "Multi-channel client monitoring (Slack, email, WhatsApp)",
      "AI urgency triage and prioritization",
      "Contextual response drafting from conversation history",
      "Automated follow-up scheduling",
      "Client health dashboard",
      "CRM auto-sync with HubSpot",
    ],
    architecture: [
      "OpenClaw monitors Slack, email, and WhatsApp channels",
      "Incoming messages classified by urgency and client",
      "CRM context pulled from HubSpot for response drafting",
      "Draft responses generated with full conversation context",
      "Follow-ups scheduled automatically for pending items",
      "Daily client health summary sent to dashboard",
    ],
  },
];
