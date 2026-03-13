"""Generate DALL-E image prompts from social media content.

Takes the generated post text and produces a descriptive prompt suitable for
DALL-E image generation, tailored to the platform and brand aesthetic.
"""

from __future__ import annotations

import logging
from typing import Optional

from openai import AsyncOpenAI

from ..config import Settings, get_settings
from ..models.content import Platform

logger = logging.getLogger(__name__)

# Visual style hints per platform.
PLATFORM_VISUAL_STYLES: dict[Platform, str] = {
    Platform.LINKEDIN: (
        "Clean, professional corporate photography or modern flat illustration. "
        "Use a blue-toned color palette. Suitable as a LinkedIn post banner."
    ),
    Platform.TWITTER: (
        "Eye-catching, bold graphic or photo with strong contrast. "
        "Square or landscape aspect ratio optimised for Twitter cards."
    ),
    Platform.INSTAGRAM: (
        "Vibrant, high-quality lifestyle or aesthetic photography. "
        "Square (1:1) composition with warm, cohesive colour grading."
    ),
    Platform.FACEBOOK: (
        "Friendly, relatable imagery. Landscape orientation. "
        "Bright, natural lighting with approachable subjects."
    ),
    Platform.THREADS: (
        "Minimal, modern graphic or candid photo. "
        "Clean background with a single focal point."
    ),
}


class ImagePromptGenerator:
    """Creates DALL-E prompts from post content using OpenAI."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self._settings = settings or get_settings()
        self._client = AsyncOpenAI(api_key=self._settings.openai_api_key)

    async def generate_prompt(
        self,
        content: str,
        platform: Platform,
        *,
        style_override: Optional[str] = None,
    ) -> str:
        """Generate a DALL-E image prompt based on post content.

        Args:
            content: The social media post text.
            platform: Target platform (affects visual style guidance).
            style_override: Optional custom style instructions.

        Returns:
            A descriptive image prompt string suitable for DALL-E.
        """
        visual_style = style_override or PLATFORM_VISUAL_STYLES.get(
            platform, "Modern, visually appealing digital artwork."
        )

        system_prompt = (
            "You are an expert visual content strategist. "
            "Given a social media post, generate a concise DALL-E image prompt "
            "that would create an engaging companion image.\n\n"
            "Rules:\n"
            "- The prompt must be 1-3 sentences (max 200 characters).\n"
            "- Do NOT include any text or words in the image.\n"
            "- Focus on mood, composition, lighting, and subject matter.\n"
            "- Never include faces or identifiable people.\n"
            f"- Visual style guidance: {visual_style}\n\n"
            "Return ONLY the image prompt text, nothing else."
        )

        user_prompt = (
            f"Generate a DALL-E image prompt for this {platform.value} post:\n\n"
            f"{content[:500]}"
        )

        logger.info("Generating image prompt for platform=%s", platform.value)

        response = await self._client.chat.completions.create(
            model=self._settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=150,
            temperature=0.8,
        )

        return (response.choices[0].message.content or "").strip()
