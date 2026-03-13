"""OpenAI-powered social media content generator.

Generates platform-specific posts with configurable tone, length, hashtags,
and emoji usage.  Each platform has tailored system prompts and character-limit
defaults so the output is ready to publish.
"""

from __future__ import annotations

import logging
from typing import Optional

from openai import AsyncOpenAI

from ..config import Settings, get_settings
from ..models.content import (
    ContentRequest,
    ContentResponse,
    ContentStatus,
    Platform,
    Tone,
)

logger = logging.getLogger(__name__)

# Platform-specific character limits (defaults when the caller does not specify).
PLATFORM_CHAR_LIMITS: dict[Platform, int] = {
    Platform.LINKEDIN: 3000,
    Platform.TWITTER: 280,
    Platform.INSTAGRAM: 2200,
    Platform.FACEBOOK: 2000,
    Platform.THREADS: 500,
}

# Short description used inside the system prompt.
PLATFORM_DESCRIPTIONS: dict[Platform, str] = {
    Platform.LINKEDIN: (
        "LinkedIn: professional networking platform. "
        "Posts should be insightful, use line breaks for readability, "
        "and optionally include a call-to-action."
    ),
    Platform.TWITTER: (
        "Twitter / X: microblogging platform. "
        "Posts must be concise and punchy. Threads are acceptable for longer ideas."
    ),
    Platform.INSTAGRAM: (
        "Instagram: visual-first platform. "
        "Captions should complement an image, use storytelling, and include hashtags at the end."
    ),
    Platform.FACEBOOK: (
        "Facebook: social networking platform. "
        "Posts can be conversational, include questions to boost engagement, and use emoji sparingly."
    ),
    Platform.THREADS: (
        "Threads: text-based social platform by Meta. "
        "Posts should be conversational and concise, similar to Twitter but slightly more relaxed."
    ),
}

TONE_INSTRUCTIONS: dict[Tone, str] = {
    Tone.PROFESSIONAL: "Use a polished, authoritative voice suitable for industry experts.",
    Tone.CASUAL: "Write in a friendly, approachable, conversational style.",
    Tone.HUMOROUS: "Inject wit and light humour while keeping the core message clear.",
    Tone.INSPIRATIONAL: "Motivate and uplift the reader with powerful, positive language.",
    Tone.EDUCATIONAL: "Teach the reader something new; use clear explanations and examples.",
    Tone.PERSUASIVE: "Convince the reader to take action; use compelling arguments and social proof.",
}


class ContentGenerator:
    """Generates social media content via OpenAI chat completions."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._client = AsyncOpenAI(api_key=self._settings.openai_api_key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate(self, request: ContentRequest) -> ContentResponse:
        """Generate a single piece of social media content.

        Args:
            request: The content generation request parameters.

        Returns:
            A ``ContentResponse`` containing the generated text and metadata.

        Raises:
            openai.APIError: If the OpenAI API call fails.
        """
        max_chars = request.max_length or PLATFORM_CHAR_LIMITS.get(request.platform, 2000)
        system_prompt = self._build_system_prompt(request, max_chars)
        user_prompt = self._build_user_prompt(request)

        logger.info(
            "Generating content for platform=%s tone=%s topic=%.60s",
            request.platform.value,
            request.tone.value,
            request.topic,
        )

        response = await self._client.chat.completions.create(
            model=self._settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=self._settings.openai_max_tokens,
            temperature=self._settings.openai_temperature,
        )

        raw_text = response.choices[0].message.content or ""
        content_text, hashtags = self._extract_hashtags(raw_text)

        return ContentResponse(
            topic=request.topic,
            platform=request.platform,
            tone=request.tone,
            content=content_text.strip(),
            hashtags=hashtags if request.include_hashtags else [],
            character_count=len(content_text.strip()),
            status=ContentStatus.DRAFT,
        )

    # ------------------------------------------------------------------
    # Prompt builders
    # ------------------------------------------------------------------

    def _build_system_prompt(self, request: ContentRequest, max_chars: int) -> str:
        """Compose the system prompt with platform and tone context."""
        platform_desc = PLATFORM_DESCRIPTIONS.get(request.platform, "Social media platform.")
        tone_instr = TONE_INSTRUCTIONS.get(request.tone, "")

        parts = [
            "You are an expert social media content creator.",
            f"Target platform: {platform_desc}",
            f"Tone: {tone_instr}",
            f"Maximum character count for the post body: {max_chars}.",
        ]

        if request.include_hashtags:
            parts.append(
                "Include 3-5 relevant hashtags at the very end of the post, "
                "each prefixed with '#'."
            )
        else:
            parts.append("Do NOT include any hashtags.")

        if not request.include_emoji:
            parts.append("Do NOT use any emoji characters.")

        if request.language != "en":
            parts.append(f"Write entirely in the language with ISO code '{request.language}'.")

        if request.additional_context:
            parts.append(f"Additional brand/content guidelines: {request.additional_context}")

        parts.append(
            "Return ONLY the post content (including hashtags if requested). "
            "Do not add explanations, labels, or commentary."
        )

        return "\n".join(parts)

    @staticmethod
    def _build_user_prompt(request: ContentRequest) -> str:
        """Compose the user prompt from topic and keywords."""
        prompt = f"Write a {request.platform.value} post about: {request.topic}"
        if request.keywords:
            prompt += f"\nKeywords to incorporate: {', '.join(request.keywords)}"
        return prompt

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_hashtags(text: str) -> tuple[str, list[str]]:
        """Separate trailing hashtags from the main body.

        Returns:
            A tuple of (body_text, list_of_hashtags).
        """
        lines = text.strip().splitlines()
        hashtags: list[str] = []
        body_lines: list[str] = []
        collecting_tags = True

        for line in reversed(lines):
            stripped = line.strip()
            if collecting_tags and stripped and all(
                token.startswith("#") for token in stripped.split()
            ):
                hashtags.extend(
                    token for token in stripped.split() if token.startswith("#")
                )
            else:
                collecting_tags = False
                body_lines.append(line)

        body_lines.reverse()
        hashtags.reverse()
        return "\n".join(body_lines), hashtags
