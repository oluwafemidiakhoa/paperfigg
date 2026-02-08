from __future__ import annotations

from importlib import resources


def load_prompt(name: str) -> str:
    prompt_file = resources.files("paperfig.prompts") / name
    return prompt_file.read_text(encoding="utf-8")
