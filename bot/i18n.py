import json
import os
from functools import lru_cache

_BASE = os.path.join(os.path.dirname(__file__), "..", "i18n")


@lru_cache(maxsize=3)
def load(lang: str) -> dict:
    path = os.path.join(_BASE, f"{lang}.json")
    if not os.path.exists(path):
        path = os.path.join(_BASE, "uz.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def t(lang: str, key: str) -> str:
    return load(lang).get(key, key)
