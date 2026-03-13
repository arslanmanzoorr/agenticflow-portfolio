"""Whisper API integration for audio transcription."""

import logging
import math
from pathlib import Path

from openai import AsyncOpenAI

from src.config import get_settings
from src.models.meeting import Transcript, TranscriptSegment

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = {".mp3", ".wav", ".m4a", ".mp4", ".webm", ".ogg", ".flac"}
CHUNK_SIZE_MB = 24  # Whisper API limit is 25 MB; use 24 to leave headroom


class TranscriptionError(Exception):
    """Raised when transcription fails."""


class TranscriberService:
    """Handles audio transcription via the OpenAI Whisper API."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.whisper_model

    async def transcribe(self, audio_path: Path) -> Transcript:
        """Transcribe an audio file and return a structured Transcript.

        For files exceeding the Whisper size limit the audio is split into
        chunks and each chunk is transcribed separately before merging.
        """
        if audio_path.suffix.lower() not in SUPPORTED_FORMATS:
            raise TranscriptionError(
                f"Unsupported audio format: {audio_path.suffix}. "
                f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
            )

        if not audio_path.exists():
            raise TranscriptionError(f"Audio file not found: {audio_path}")

        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        logger.info(
            "Starting transcription",
            extra={"file": audio_path.name, "size_mb": round(file_size_mb, 2)},
        )

        if file_size_mb <= CHUNK_SIZE_MB:
            return await self._transcribe_single(audio_path)

        return await self._transcribe_chunked(audio_path, file_size_mb)

    async def _transcribe_single(self, audio_path: Path) -> Transcript:
        """Transcribe a single audio file that fits within the API size limit."""
        try:
            with open(audio_path, "rb") as audio_file:
                response = await self._client.audio.transcriptions.create(
                    model=self._model,
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                )

            segments = [
                TranscriptSegment(
                    start=seg.get("start", 0.0),
                    end=seg.get("end", 0.0),
                    text=seg.get("text", "").strip(),
                )
                for seg in (response.segments or [])
            ]

            duration = response.duration or (
                segments[-1].end if segments else 0.0
            )

            logger.info(
                "Transcription complete",
                extra={
                    "file": audio_path.name,
                    "duration_s": round(duration, 1),
                    "segments": len(segments),
                },
            )

            return Transcript(
                full_text=response.text.strip(),
                segments=segments,
                language=response.language or "en",
                duration_seconds=duration,
            )

        except Exception as exc:
            logger.error("Transcription failed: %s", exc, exc_info=True)
            raise TranscriptionError(f"Whisper API error: {exc}") from exc

    async def _transcribe_chunked(
        self, audio_path: Path, file_size_mb: float
    ) -> Transcript:
        """Split a large file into chunks and transcribe each one.

        This is a simplified chunking strategy that reads the file in byte
        ranges.  For production use, consider using ffmpeg to split on silence
        boundaries so words are not cut mid-utterance.
        """
        chunk_count = math.ceil(file_size_mb / CHUNK_SIZE_MB)
        logger.info(
            "File exceeds size limit, splitting into %d chunks", chunk_count
        )

        all_segments: list[TranscriptSegment] = []
        all_texts: list[str] = []
        total_duration = 0.0
        detected_language = "en"

        chunk_bytes = CHUNK_SIZE_MB * 1024 * 1024
        raw = audio_path.read_bytes()

        for i in range(chunk_count):
            start = i * chunk_bytes
            end = min((i + 1) * chunk_bytes, len(raw))
            chunk_path = audio_path.with_suffix(f".chunk{i}{audio_path.suffix}")

            try:
                chunk_path.write_bytes(raw[start:end])

                with open(chunk_path, "rb") as chunk_file:
                    response = await self._client.audio.transcriptions.create(
                        model=self._model,
                        file=chunk_file,
                        response_format="verbose_json",
                        timestamp_granularities=["segment"],
                    )

                offset = total_duration
                for seg in response.segments or []:
                    all_segments.append(
                        TranscriptSegment(
                            start=seg.get("start", 0.0) + offset,
                            end=seg.get("end", 0.0) + offset,
                            text=seg.get("text", "").strip(),
                        )
                    )

                all_texts.append(response.text.strip())
                chunk_duration = response.duration or 0.0
                total_duration += chunk_duration
                detected_language = response.language or detected_language

                logger.info(
                    "Chunk %d/%d transcribed (%0.1fs)",
                    i + 1,
                    chunk_count,
                    chunk_duration,
                )
            finally:
                chunk_path.unlink(missing_ok=True)

        return Transcript(
            full_text=" ".join(all_texts),
            segments=all_segments,
            language=detected_language,
            duration_seconds=total_duration,
        )
