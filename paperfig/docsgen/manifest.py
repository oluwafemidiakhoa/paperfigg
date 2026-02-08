from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from paperfig.utils.structured_data import load_structured_file


@dataclass
class DocManifestEntry:
    path: str
    mode: str
    required_sections: List[str] = field(default_factory=list)


@dataclass
class DocsManifest:
    documents: List[DocManifestEntry]
    auto_blocks: Dict[str, Dict[str, Any]] = field(default_factory=dict)


VALID_MODES = {"generated", "hybrid", "validated"}


def load_manifest(path: Path) -> DocsManifest:
    data = load_structured_file(path)
    if not isinstance(data, dict):
        raise RuntimeError(f"Manifest at {path} must contain a mapping/object.")

    docs_data = data.get("documents", [])
    if not isinstance(docs_data, list):
        raise RuntimeError("Manifest 'documents' must be a list.")

    entries: List[DocManifestEntry] = []
    for item in docs_data:
        if not isinstance(item, dict):
            raise RuntimeError("Each manifest document entry must be a mapping/object.")
        mode = str(item.get("mode", "validated"))
        if mode not in VALID_MODES:
            raise RuntimeError(f"Invalid document mode '{mode}'. Expected one of {sorted(VALID_MODES)}.")
        required = item.get("required_sections", [])
        if not isinstance(required, list):
            raise RuntimeError("required_sections must be a list.")
        entries.append(
            DocManifestEntry(
                path=str(item.get("path", "")),
                mode=mode,
                required_sections=[str(section) for section in required],
            )
        )

    auto_blocks = data.get("auto_blocks", {})
    if not isinstance(auto_blocks, dict):
        raise RuntimeError("Manifest 'auto_blocks' must be a mapping/object.")

    return DocsManifest(documents=entries, auto_blocks=auto_blocks)
