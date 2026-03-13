"""OpenAI-powered sentiment analysis service.

Analyses review text to produce:
- Overall sentiment score (-1 to 1)
- Category-level scores (service, quality, price, ambiance, etc.)
- Key phrase extraction
- One-sentence summary
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from openai import AsyncOpenAI

from api.src.config import Settings
from api.src.models.review import (
    AnalyzeRequest,
    AnalyzeResponse,
    CategoryScore,
    Review,
    ReviewCategory,
    SentimentLabel,
    SentimentResult,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a sentiment analysis engine specialising in customer reviews.

For each review you receive, return a JSON object with the following structure:

{
  "overall_score": <float -1.0 to 1.0>,
  "label": "<positive|neutral|negative>",
  "confidence": <float 0.0 to 1.0>,
  "categories": [
    {
      "category": "<service|quality|price|ambiance|cleanliness|speed|communication|value>",
      "score": <float -1.0 to 1.0>,
      "confidence": <float 0.0 to 1.0>,
      "mentions": ["<exact phrase from review>"]
    }
  ],
  "key_phrases": ["<important phrases from the review>"],
  "summary": "<one concise sentence summarising the review sentiment>"
}

Rules:
- Only include categories that are explicitly or strongly implicitly mentioned.
- Scores: -1.0 = extremely negative, 0.0 = neutral, 1.0 = extremely positive.
- Extract 2-5 key phrases that capture the reviewer's main points.
- The summary should be objective and factual.
- Return ONLY valid JSON, no markdown fences or extra text.
"""

BATCH_SYSTEM_PROMPT = """\
You are a sentiment analysis engine. You will receive multiple reviews separated by
"---REVIEW---" markers. For each review, return a JSON object on its own line.
Return ONLY a JSON array of objects, no markdown fences or extra text.
Each object follows this schema:

{
  "review_index": <int>,
  "overall_score": <float -1.0 to 1.0>,
  "label": "<positive|neutral|negative>",
  "confidence": <float 0.0 to 1.0>,
  "categories": [
    {
      "category": "<service|quality|price|ambiance|cleanliness|speed|communication|value>",
      "score": <float -1.0 to 1.0>,
      "confidence": <float 0.0 to 1.0>,
      "mentions": ["<exact phrase>"]
    }
  ],
  "key_phrases": ["<phrase>"],
  "summary": "<one sentence>"
}
"""


class SentimentAnalyzer:
    """Analyse review sentiment using OpenAI chat completions."""

    def __init__(self, settings: Settings) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self._settings = settings

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def analyze_single(
        self,
        review: Review,
        *,
        include_categories: bool = True,
        include_key_phrases: bool = True,
        include_summary: bool = True,
    ) -> SentimentResult:
        """Analyse a single review."""
        user_content = self._build_single_prompt(
            review, include_categories, include_key_phrases, include_summary
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.1,
            max_tokens=800,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        parsed = self._parse_result(raw, review.review_id)
        parsed.model_used = self.model
        return parsed

    async def analyze_batch(self, request: AnalyzeRequest) -> AnalyzeResponse:
        """Analyse a batch of reviews efficiently.

        Reviews are grouped into sub-batches of 10 to stay within token
        limits while minimising API calls.
        """
        start = time.monotonic()
        results: list[SentimentResult] = []
        batch_size = 10

        for i in range(0, len(request.reviews), batch_size):
            batch = request.reviews[i : i + batch_size]
            batch_results = await self._analyze_sub_batch(
                batch,
                include_categories=request.include_categories,
                include_key_phrases=request.include_key_phrases,
                include_summary=request.include_summary,
            )
            results.extend(batch_results)

        elapsed = (time.monotonic() - start) * 1000

        return AnalyzeResponse(
            results=results,
            processing_time_ms=round(elapsed, 2),
            total_analyzed=len(results),
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    async def _analyze_sub_batch(
        self,
        reviews: list[Review],
        *,
        include_categories: bool,
        include_key_phrases: bool,
        include_summary: bool,
    ) -> list[SentimentResult]:
        if len(reviews) == 1:
            return [
                await self.analyze_single(
                    reviews[0],
                    include_categories=include_categories,
                    include_key_phrases=include_key_phrases,
                    include_summary=include_summary,
                )
            ]

        prompt_parts: list[str] = []
        for idx, review in enumerate(reviews):
            prompt_parts.append(
                f"---REVIEW---\nIndex: {idx}\n"
                f"Rating: {review.rating}/{review.max_rating}\n"
                f"Text: {review.text}\n"
            )

        user_content = "\n".join(prompt_parts)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": BATCH_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.1,
                max_tokens=len(reviews) * 600,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content or "[]"
            return self._parse_batch_results(raw, reviews)
        except Exception:
            logger.exception("Batch analysis failed, falling back to individual")
            results = []
            for review in reviews:
                try:
                    r = await self.analyze_single(
                        review,
                        include_categories=include_categories,
                        include_key_phrases=include_key_phrases,
                        include_summary=include_summary,
                    )
                    results.append(r)
                except Exception:
                    logger.exception("Failed to analyse review %s", review.review_id)
                    results.append(self._fallback_result(review.review_id))
            return results

    def _build_single_prompt(
        self,
        review: Review,
        include_categories: bool,
        include_key_phrases: bool,
        include_summary: bool,
    ) -> str:
        parts = [
            f"Platform: {review.platform.value}",
            f"Rating: {review.rating}/{review.max_rating}",
            f"Date: {review.date}",
            f"Review text: {review.text}",
        ]
        omissions = []
        if not include_categories:
            omissions.append("categories")
        if not include_key_phrases:
            omissions.append("key_phrases")
        if not include_summary:
            omissions.append("summary")
        if omissions:
            parts.append(
                f"\nOmit these fields (return empty): {', '.join(omissions)}"
            )
        return "\n".join(parts)

    def _parse_result(self, raw_json: str, review_id: str) -> SentimentResult:
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON from OpenAI for review %s", review_id)
            return self._fallback_result(review_id)

        categories = []
        for cat_data in data.get("categories", []):
            try:
                categories.append(
                    CategoryScore(
                        category=ReviewCategory(cat_data["category"]),
                        score=float(cat_data.get("score", 0)),
                        confidence=float(cat_data.get("confidence", 0)),
                        mentions=cat_data.get("mentions", []),
                    )
                )
            except (KeyError, ValueError):
                continue

        score = float(data.get("overall_score", 0))
        label_str = data.get("label", "neutral")
        try:
            label = SentimentLabel(label_str)
        except ValueError:
            label = (
                SentimentLabel.POSITIVE
                if score > 0.2
                else SentimentLabel.NEGATIVE
                if score < -0.2
                else SentimentLabel.NEUTRAL
            )

        return SentimentResult(
            review_id=review_id,
            overall_score=max(-1, min(1, score)),
            label=label,
            confidence=float(data.get("confidence", 0.5)),
            categories=categories,
            key_phrases=data.get("key_phrases", []),
            summary=data.get("summary", ""),
            model_used=self.model,
        )

    def _parse_batch_results(
        self, raw_json: str, reviews: list[Review]
    ) -> list[SentimentResult]:
        try:
            data = json.loads(raw_json)
            # Handle {"results": [...]} wrapper
            if isinstance(data, dict):
                data = data.get("results", data.get("reviews", []))
            if not isinstance(data, list):
                data = [data]
        except json.JSONDecodeError:
            logger.warning("Invalid batch JSON from OpenAI")
            return [self._fallback_result(r.review_id) for r in reviews]

        results: list[SentimentResult] = []
        for idx, review in enumerate(reviews):
            matching = [
                d for d in data if d.get("review_index") == idx
            ]
            if matching:
                item = matching[0]
                item_json = json.dumps(item)
                results.append(self._parse_result(item_json, review.review_id))
            elif idx < len(data):
                item_json = json.dumps(data[idx])
                results.append(self._parse_result(item_json, review.review_id))
            else:
                results.append(self._fallback_result(review.review_id))

        return results

    @staticmethod
    def _fallback_result(review_id: str) -> SentimentResult:
        return SentimentResult(
            review_id=review_id,
            overall_score=0.0,
            label=SentimentLabel.NEUTRAL,
            confidence=0.0,
            categories=[],
            key_phrases=[],
            summary="Analysis could not be completed.",
            model_used="fallback",
        )
