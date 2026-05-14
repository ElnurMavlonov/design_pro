SYSTEM_PROMPT = """\
You are an expert presentation designer for Uzbek teachers and students.
Your job is to generate presentation content and return ONLY valid JSON — no markdown, no explanation, no code fences.

The JSON must follow this exact schema:
{
  "title": "Main presentation title",
  "subtitle": "Optional subtitle or author/class info",
  "theme": "education|science|history|technology|default",
  "language": "uz|ru|en",
  "slides": [
    {
      "title": "Slide title",
      "body": ["Bullet point 1", "Bullet point 2", "Bullet point 3"],
      "speaker_notes": "Brief notes for the presenter"
    }
  ]
}

Rules:
- First slide must be a title/intro slide (body can be empty or have 1-2 intro points)
- Last slide should be a summary or conclusion slide
- Each body list should have 3-6 concise bullet points
- Bullet points must be clear, educational, and age-appropriate
- Match the language of the content to the requested language
- Choose the theme based on the subject matter
- speaker_notes should be 1-2 sentences max
- Return ONLY the JSON object, nothing else
"""

GRADE_LABELS = {
    "primary": {"uz": "Boshlang'ich sinf (1-4)", "ru": "Начальная школа (1-4)", "en": "Primary school (grades 1-4)"},
    "middle": {"uz": "O'rta maktab (5-9)", "ru": "Средняя школа (5-9)", "en": "Middle school (grades 5-9)"},
    "high": {"uz": "Yuqori sinf (10-11)", "ru": "Старшие классы (10-11)", "en": "High school (grades 10-11)"},
    "university": {"uz": "Universitet", "ru": "Университет", "en": "University"},
}

TONE_LABELS = {
    "formal": {"uz": "rasmiy", "ru": "официальный", "en": "formal"},
    "simple": {"uz": "oddiy va tushunarli", "ru": "простой и понятный", "en": "simple and clear"},
    "fun": {"uz": "qiziqarli va jonli", "ru": "весёлый и живой", "en": "fun and engaging"},
}

LANG_LABELS = {
    "uz": "O'zbek tilida",
    "ru": "На русском языке",
    "en": "In English",
}


def build_quick_prompt(user_input: str, lang: str) -> str:
    return (
        f"Create a presentation based on this description: {user_input}\n\n"
        f"Content language: {LANG_LABELS.get(lang, 'O\'zbek tilida')}\n"
        f"Return only the JSON object."
    )


def build_wizard_prompt(topic: str, slides: int, grade: str, tone: str, lang: str) -> str:
    grade_label = GRADE_LABELS.get(grade, GRADE_LABELS["middle"])[lang]
    tone_label = TONE_LABELS.get(tone, TONE_LABELS["simple"])[lang]
    lang_label = LANG_LABELS.get(lang, "O'zbek tilida")

    return (
        f"Create a presentation with the following parameters:\n"
        f"- Topic: {topic}\n"
        f"- Number of slides: {slides}\n"
        f"- Audience: {grade_label}\n"
        f"- Tone/style: {tone_label}\n"
        f"- Content language: {lang_label}\n\n"
        f"Return only the JSON object."
    )
