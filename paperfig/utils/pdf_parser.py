from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from .types import PaperContent, PaperSection


_HEADING_RE = re.compile(r"(?m)^(\d+\.?\s+)?([A-Za-z][A-Za-z0-9 \-]{0,80})\s*$")


def _extract_text_pdf(path: Path) -> str:
    errors: List[str] = []

    try:
        from pdfminer.high_level import extract_text  # type: ignore

        return extract_text(str(path))
    except Exception as exc:  # pragma: no cover - optional dependency
        errors.append(f"pdfminer.six failed: {exc}")

    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        text_parts = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(text_parts)
    except Exception as exc:  # pragma: no cover - optional dependency
        errors.append(f"pypdf failed: {exc}")

    raise RuntimeError(
        "PDF parsing failed. Install pdfminer.six or pypdf. Details: " + "; ".join(errors)
    )


def extract_text(path: Path) -> str:
    if path.suffix.lower() in {".md", ".markdown"}:
        return path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".pdf":
        return _extract_text_pdf(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")


def _find_headings(text: str) -> List[Dict[str, int | str]]:
    headings: List[Dict[str, int | str]] = []
    for match in _HEADING_RE.finditer(text):
        label = match.group(2).strip()
        # Filter out headings that are too long or likely paragraph lines.
        if len(label.split()) > 10:
            continue
        headings.append({"start": match.start(), "end": match.end(), "label": label})
    return headings


def _extract_section(text: str, name: str, keywords: List[str]) -> PaperSection:
    headings = _find_headings(text)
    for idx, heading in enumerate(headings):
        label = str(heading["label"]).lower()
        if any(keyword in label for keyword in keywords):
            start = int(heading["end"])
            end = int(headings[idx + 1]["start"]) if idx + 1 < len(headings) else len(text)
            section_text = text[start:end].strip()
            return PaperSection(name=name, text=section_text, start=start, end=end)

    # Fallback: find first keyword occurrence and capture a window
    lowered = text.lower()
    positions = [lowered.find(keyword) for keyword in keywords if lowered.find(keyword) != -1]
    if positions:
        idx = min(positions)
        start = max(0, idx - 500)
        end = min(len(text), idx + 2000)
        return PaperSection(name=name, text=text[start:end].strip(), start=start, end=end)

    return PaperSection(name=name, text="", start=0, end=0)


def extract_sections(text: str) -> Dict[str, PaperSection]:
    methodology = _extract_section(
        text,
        name="methodology",
        keywords=["method", "methods", "methodology", "approach"],
    )
    system = _extract_section(
        text,
        name="system",
        keywords=["system", "architecture", "model", "pipeline"],
    )
    results = _extract_section(
        text,
        name="results",
        keywords=["results", "experiments", "evaluation"],
    )
    return {
        "methodology": methodology,
        "system": system,
        "results": results,
    }


def parse_paper(path: Path) -> PaperContent:
    text = extract_text(path)
    sections = extract_sections(text)
    return PaperContent(source_path=str(path), full_text=text, sections=sections)
