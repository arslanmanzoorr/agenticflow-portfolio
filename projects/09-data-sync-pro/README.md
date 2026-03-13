# DataSync Pro - Multi-Database Sync Engine

Automated bidirectional data synchronization engine built with n8n, orchestrating seamless sync between Airtable, Google Sheets, and PostgreSQL with configurable field mappings, conflict resolution, and real-time Slack notifications.

## Tools & Technologies

- **n8n** - Workflow automation and orchestration
- **Airtable** - Cloud database / CRM data source
- **Google Sheets** - Spreadsheet data source and reporting layer
- **PostgreSQL** - Relational database for transactional data
- **Slack** - Real-time sync notifications and error alerts

## Architecture

```
                    +------------------+
                    |   n8n Scheduler  |
                    |  (Every 15 min)  |
                    +--------+---------+
                             |
                    +--------v---------+
                    | Sync Mappings    |
                    | Configuration    |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+   +-----v------+  +----v--------+
     |  Airtable  |   |  Google    |  | PostgreSQL  |
     |  Records   |   |  Sheets   |  |  Tables     |
     +--------+---+   +-----+------+  +----+--------+
              |              |              |
              +--------------+--------------+
                             |
                    +--------v---------+
                    | Field Transform  |
                    | & Mapping Engine |
                    +--------+---------+
                             |
                    +--------v---------+
                    | Conflict Resolver|
                    | (latest_wins /   |
                    |  source_wins)    |
                    +--------+---------+
                             |
                    +--------v---------+
                    | Slack Alerts     |
                    +------------------+
```

## Included Workflows

### 1. Bidirectional Sync (`bidirectional-sync.json`)
Two-way synchronization between Airtable and Google Sheets. Detects changes on both sides, applies field transformations, and uses the configured conflict resolution strategy when the same record has been modified in both systems.

### 2. PostgreSQL ETL (`postgres-etl.json`)
Incremental ETL pipeline that extracts new and updated records from PostgreSQL, transforms them according to field mappings, and loads them into Airtable. Supports incremental sync using timestamp-based change detection.

### 3. Conflict Resolver (`conflict-resolver.json`)
Dedicated conflict detection and resolution workflow. Compares records across data sources, identifies conflicts based on sync keys, and applies the configured resolution strategy (latest_wins, source_wins, or manual review). Logs all conflict resolutions for audit.

### 4. Scheduled Sync (`scheduled-sync.json`)
Master orchestration workflow that runs every 15 minutes. Reads the sync mappings configuration, splits work into individual sync jobs, executes field transformations, updates destination systems, and sends a Slack summary upon completion. Includes error handling with Slack error notifications.

## Configuration

### Sync Mappings (`configs/sync-mappings.json`)

The sync mappings file defines how data flows between systems. Each mapping includes:

- **name** - Unique identifier for the sync job
- **source / destination** - Data source type and table/sheet reference
- **fields** - Array of field mappings with optional transforms
- **sync_direction** - `bidirectional` or `source_to_destination`
- **sync_key** - Field used to match records across systems
- **conflict_resolution** - Strategy when both sides have changes

#### Supported Field Transforms

| Transform | Description |
|-----------|-------------|
| `none` | Pass through without modification |
| `lowercase` | Convert string to lowercase |
| `uppercase` | Convert string to uppercase |
| `capitalize` | Capitalize first letter |
| `date_format` | Format date with specified pattern |
| `integer` | Parse as integer |
| `decimal` | Parse as decimal |
| `currency` | Format as currency string |
| `join` | Join array with delimiter |
| `map` | Map values using lookup table |
| `json_stringify` | Serialize object to JSON string |
| `timestamp` | Parse as ISO timestamp |

### Credentials (`configs/credentials-template.json`)

Copy and rename to `credentials/google-sheets.json`, then replace placeholder values with your Google Cloud service account credentials.

## Conflict Resolution Strategies

| Strategy | Behavior |
|----------|----------|
| `latest_wins` | The most recently modified record takes precedence |
| `source_wins` | Source system always overwrites destination |
| `manual_review` | Conflicts are flagged in Slack for manual resolution |

## Setup

1. **Clone and configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database credentials
   ```

2. **Set up Google Sheets credentials**
   ```bash
   cp configs/credentials-template.json credentials/google-sheets.json
   # Replace with your service account credentials
   ```

3. **Configure sync mappings**
   Edit `configs/sync-mappings.json` to define your field mappings, sync directions, and conflict resolution preferences.

4. **Import workflows into n8n**
   Import all JSON files from the `workflows/` directory into your n8n instance.

5. **Set environment variables in n8n**
   Add all variables from `.env.example` to your n8n environment configuration.

6. **Activate the Scheduled Sync workflow**
   Enable the scheduled sync workflow to begin automated synchronization.

## Error Handling

All workflows include error handling that sends detailed Slack notifications to the `#data-sync-alerts` channel. Errors include the failing node, error message, and timestamp for rapid debugging. Failed sync jobs are automatically retried up to 3 times with a 5-second delay between attempts.
