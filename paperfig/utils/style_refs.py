from __future__ import annotations

import json
import os
from importlib import resources
from pathlib import Path
from typing import Any, Dict


def load_style_refs(name: str = "conference_default.json") -> Dict[str, Any]:
    """
    Load style references from either a file path (PAPERFIG_STYLE_REF)
    or from packaged defaults in paperfig/styles.
    """
    override = os.getenv("PAPERFIG_STYLE_REF")
    if override:
        path = Path(override)
        if not path.exists():
            raise FileNotFoundError(f"Style reference file not found: {override}")
        return json.loads(path.read_text(encoding="utf-8"))

    style_file = resources.files("paperfig.styles") / name
    return json.loads(style_file.read_text(encoding="utf-8"))
