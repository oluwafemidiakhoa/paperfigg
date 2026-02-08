from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List

from .manifest import DocsManifest, load_manifest
from .renderer import render_hybrid_document


def _validate_required_sections(text: str, required_sections: List[str]) -> List[str]:
    missing: List[str] = []
    for section in required_sections:
        if section not in text:
            missing.append(section)
    return missing


def run_docs_regeneration(
    manifest_path: Path,
    check_only: bool,
    repo_root: Path,
) -> Dict[str, Any]:
    manifest: DocsManifest = load_manifest(manifest_path)
    doc_reports: List[Dict[str, Any]] = []
    drift_detected = False

    for entry in manifest.documents:
        doc_path = repo_root / entry.path
        report: Dict[str, Any] = {
            "path": entry.path,
            "mode": entry.mode,
            "exists": doc_path.exists(),
            "drift": False,
            "written": False,
            "missing_required_sections": [],
            "rendered_blocks": [],
            "missing_block_configs": [],
            "error": "",
        }

        if not doc_path.exists():
            report["error"] = "document_missing"
            drift_detected = True
            doc_reports.append(report)
            continue

        try:
            original = doc_path.read_text(encoding="utf-8")
            rendered = original

            if entry.mode in {"hybrid", "generated"}:
                rendered, rendered_blocks, missing_block_configs = render_hybrid_document(
                    original,
                    manifest.auto_blocks,
                    repo_root,
                )
                report["rendered_blocks"] = rendered_blocks
                report["missing_block_configs"] = missing_block_configs
                if missing_block_configs:
                    report["error"] = "missing_block_config"

            missing_sections = _validate_required_sections(rendered, entry.required_sections)
            report["missing_required_sections"] = missing_sections
            if missing_sections:
                report["error"] = "missing_required_sections"

            if rendered != original:
                report["drift"] = True
                drift_detected = True
                if not check_only:
                    doc_path.write_text(rendered, encoding="utf-8")
                    report["written"] = True
        except Exception as exc:  # pragma: no cover - defensive
            report["error"] = str(exc)
            drift_detected = True

        doc_reports.append(report)

    return {
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "manifest_path": str(manifest_path),
        "check_only": check_only,
        "drift_detected": drift_detected,
        "documents": doc_reports,
    }
