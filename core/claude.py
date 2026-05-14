import json
import logging
import os
import re

from groq import AsyncGroq

from core.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_client: AsyncGroq | None = None


def get_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])
    return _client


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def generate_presentation(user_prompt: str, retrying: bool = False) -> dict:
    client = get_client()

    strict_suffix = "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanation." if retrying else ""

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt + strict_suffix},
        ],
        max_tokens=4096,
        temperature=0.7,
    )

    raw = response.choices[0].message.content
    logger.info("Groq raw response (first 200 chars): %s", raw[:200])

    try:
        data = _extract_json(raw)
    except (json.JSONDecodeError, IndexError) as exc:
        logger.error("JSON parse failed: %s | raw: %s", exc, raw[:500])
        if not retrying:
            return await generate_presentation(user_prompt, retrying=True)
        raise ValueError(f"Groq returned invalid JSON after retry: {exc}") from exc

    if "slides" not in data or not isinstance(data["slides"], list):
        raise ValueError("Response missing 'slides' array")

    return data
