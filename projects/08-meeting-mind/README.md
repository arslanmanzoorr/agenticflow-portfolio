# MeetingMind - AI Meeting Notes Automation

End-to-end system that transforms meeting audio recordings into structured notes, summaries, and action items, then distributes them via Slack and email.

## Tools & Technologies

- **Python / FastAPI** - Async REST API
- **OpenAI Whisper** - Audio-to-text transcription
- **OpenAI GPT-4** - Summarization and action item extraction
- **Airtable** - Persistent storage for meetings and action items
- **Slack SDK** - Post meeting recaps to channels
- **SMTP / aiosmtplib** - Email distribution
- **Docker** - Containerized deployment with FFmpeg

## How It Works

```
Upload Audio ──> Whisper Transcription ──> GPT Summarization
                                               │
                                    ┌──────────┼──────────┐
                                    ▼          ▼          ▼
                              Action Item   Airtable   Slack / Email
                              Extraction    Storage    Distribution
```

1. **Upload** an audio file (MP3, WAV, M4A, etc.) to the `/transcribe` endpoint
2. **Whisper** transcribes the audio into timestamped text segments
3. **GPT-4** generates a structured summary with executive overview, key decisions, and discussion topics
4. **GPT-4** extracts action items with assignees, deadlines, and priority levels
5. Results are **stored in Airtable** for long-term tracking
6. Meeting notes are **shared via Slack** and/or **email** to participants

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/transcribe` | Upload audio file for Whisper transcription |
| `POST` | `/summarize` | Generate GPT summary from transcript text |
| `POST` | `/action-items` | Extract action items from transcript text |
| `GET` | `/meetings` | List all processed meetings |
| `GET` | `/meetings/{id}` | Get meeting details with transcript, summary, and actions |
| `POST` | `/meetings/{id}/share` | Share meeting notes via Slack and/or email |

### Request Examples

**POST /transcribe** - Multipart file upload
```
Content-Type: multipart/form-data
file: <audio_file.mp3>
```

**POST /summarize**
```json
{
  "transcript_text": "Full transcript text...",
  "meeting_id": "optional-meeting-id"
}
```

**POST /action-items**
```json
{
  "transcript_text": "Full transcript text...",
  "meeting_id": "optional-meeting-id"
}
```

**POST /meetings/{id}/share**
```json
{
  "channel": "#team-standup",
  "email_recipients": ["alice@company.com", "bob@company.com"],
  "include_transcript": false,
  "include_action_items": true
}
```

## Setup

### Prerequisites

- Python 3.11+
- FFmpeg (required for audio processing)
- OpenAI API key
- Airtable base with `Meetings` and `ActionItems` tables
- Slack bot token (optional)
- SMTP credentials (optional)

### Environment Variables

```bash
cp .env.example .env
# Edit .env with your credentials
```

### Local Development

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### Docker

```bash
docker build -t meeting-mind .
docker run -p 8000:8000 --env-file .env meeting-mind
```

### Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

### Airtable Setup

Create a base with two tables:

**Meetings** - `MeetingID`, `Title`, `AudioFilename`, `FullTranscript`, `ExecutiveSummary`, `KeyDecisions`, `DiscussionTopics`, `Participants`, `Status`, `CreatedAt`

**ActionItems** - `MeetingID`, `Description`, `AssignedTo`, `Deadline`, `Priority`, `Status`

## Project Structure

```
08-meeting-mind/
├── src/
│   ├── __init__.py
│   ├── config.py                # Pydantic settings
│   ├── main.py                  # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   └── meeting.py           # Pydantic domain models
│   └── services/
│       ├── __init__.py
│       ├── transcriber.py       # OpenAI Whisper integration
│       ├── summarizer.py        # GPT summarization
│       ├── action_extractor.py  # GPT action item extraction
│       ├── airtable_client.py   # Airtable persistence
│       └── notifier.py          # Slack + email notifications
├── tests/
│   ├── __init__.py
│   ├── test_summarizer.py       # Summarizer unit tests
│   └── test_action_extractor.py # Action extractor unit tests
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md
```
