import json
import logging
import os
import re

from google import genai
from google.genai import types

from core.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def generate_presentation(user_prompt: str, retrying: bool = False) -> dict:
    client = get_client()

    strict_suffix = "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanation." if retrying else ""

    response = await client.aio.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=user_prompt + strict_suffix,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=4096,
        ),
    )

    raw = response.text
    logger.info("Gemini raw response (first 200 chars): %s", raw[:200])

    try:
        data = _extract_json(raw)
    except (json.JSONDecodeError, IndexError) as exc:
        logger.error("JSON parse failed: %s | raw: %s", exc, raw[:500])
        if not retrying:
            return await generate_presentation(user_prompt, retrying=True)
        raise ValueError(f"Gemini returned invalid JSON after retry: {exc}") from exc

    if "slides" not in data or not isinstance(data["slides"], list):
        raise ValueError("Response missing 'slides' array")

    return data
