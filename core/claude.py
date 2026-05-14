import json
import os
import re

import anthropic

from core.prompts import SYSTEM_PROMPT

_client: anthropic.AsyncAnthropic | None = None


def get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def _extract_json(text: str) -> dict:
    """Extract JSON from response, stripping any accidental markdown fences."""
    text = text.strip()
    # Strip ```json ... ``` or ``` ... ``` if Claude adds them despite instructions
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


async def generate_presentation(user_prompt: str, retrying: bool = False) -> dict:
    """Call Claude and return parsed slide JSON."""
    client = get_client()

    system = [
        {
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }
    ]

    strict_suffix = "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanation." if retrying else ""

    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user_prompt + strict_suffix}],
    )

    raw = response.content[0].text

    try:
        data = _extract_json(raw)
    except (json.JSONDecodeError, IndexError) as exc:
        if not retrying:
            return await generate_presentation(user_prompt, retrying=True)
        raise ValueError(f"Claude returned invalid JSON after retry: {exc}") from exc

    # Basic schema validation
    if "slides" not in data or not isinstance(data["slides"], list):
        raise ValueError("Response missing 'slides' array")

    return data
