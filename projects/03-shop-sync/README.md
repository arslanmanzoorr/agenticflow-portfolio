# ShopSync - E-Commerce Order & Inventory Automation

Automated order processing, inventory management, and returns handling for Shopify stores using n8n workflows, Airtable as the operational database, and Slack for team notifications.

## Architecture

```
Shopify Store
    |
    v
n8n Workflow Engine
    |
    +---> Order Processing -----> Airtable (Orders table)
    |         |                       |
    |         +---> Slack #orders     +---> Low Stock Alert
    |                                        |
    |                                        v
    +---> Inventory Sync (6h) -----> Airtable (Inventory table)
    |         |                       |
    |         +---> Slack #inventory  +---> Daily Report
    |
    +---> Returns Handler ---------> Airtable (Returns table)
              |                       |
              +---> Slack #returns    +---> Customer Email
              +---> Return Label API
```

## Workflows

### 1. Order Processing (`workflows/order-processing.json`)
Triggered by Shopify webhook on every new order. Extracts customer and line-item data, writes an order record to Airtable, checks current inventory levels, and posts a summary to Slack. If any SKU drops below its reorder threshold, an alert is sent to `#inventory`.

### 2. Inventory Sync (`workflows/inventory-sync.json`)
Runs on a 6-hour schedule. Pulls the full product catalog from Shopify, compares quantities against Airtable inventory records, updates discrepancies, and generates a daily inventory report posted to Slack.

### 3. Returns Handler (`workflows/returns-handler.json`)
Receives return requests via webhook. Validates eligibility based on order date and item condition rules, updates the order status in Airtable, creates a return shipping label, emails the customer with return instructions, and logs the event to Slack `#returns`.

## Airtable Schema

The `schemas/airtable-base.json` file defines four tables:

| Table       | Purpose                                      |
|-------------|----------------------------------------------|
| Orders      | Every Shopify order with status tracking      |
| Inventory   | Product stock levels and reorder thresholds   |
| Returns     | Return requests linked to original orders     |
| Customers   | Customer profiles aggregated from orders      |

## Prerequisites

- **n8n** >= 1.30 (self-hosted or n8n Cloud)
- **Shopify** store with API access (Admin API key)
- **Airtable** base with tables matching the schema
- **Slack** workspace with a bot token and channels: `#orders`, `#inventory`, `#returns`
- SMTP credentials for customer-facing emails

## Setup

1. **Clone the repository** and copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. **Fill in credentials** in `.env` with your Shopify, Airtable, Slack, and SMTP values.

3. **Create the Airtable base** using the schema in `schemas/airtable-base.json` as a reference. Create each table with the listed fields and field types.

4. **Import workflows into n8n**:
   - Open your n8n instance
   - Go to Workflows > Import from File
   - Import each JSON file from the `workflows/` directory
   - Update credential references in each workflow to match your n8n credentials

5. **Configure Shopify webhooks**:
   - In Shopify Admin > Settings > Notifications > Webhooks
   - Add a webhook for `orders/create` pointing to the order-processing webhook URL
   - Add a webhook for `refunds/create` if you want automatic return triggers

6. **Create Slack channels**: `#orders`, `#inventory`, `#returns` and invite the Slack bot.

7. **Activate workflows** in n8n.

## Environment Variables

See `.env.example` for the full list. Key groups:

- `SHOPIFY_*` - Store domain and API credentials
- `AIRTABLE_*` - API key and base/table IDs
- `SLACK_*` - Bot token and channel IDs
- `SMTP_*` - Email server configuration
- `N8N_*` - n8n instance settings
- `RETURNS_*` - Return policy parameters

## Project Structure

```
03-shop-sync/
  .env.example
  README.md
  schemas/
    airtable-base.json
  workflows/
    order-processing.json
    inventory-sync.json
    returns-handler.json
```

## License

MIT
