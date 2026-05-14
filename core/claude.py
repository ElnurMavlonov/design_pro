import json
import logging
import os
import re

import google.generativeai as genai

from core.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_model: genai.GenerativeModel | None = None


def get_model() -> genai.GenerativeModel:
    global _model
    if _model is None:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        _model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=SYSTEM_PROMPT,
        )
    return _model


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def generate_presentation(user_prompt: str, retrying: bool = False) -> dict:
    model = get_model()

    strict_suffix = "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanation." if retrying else ""

    response = await model.generate_content_async(user_prompt + strict_suffix)
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
