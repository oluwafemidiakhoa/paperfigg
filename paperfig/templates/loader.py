from __future__ import annotations

import importlib.util
from importlib import resources
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from paperfig.utils.structured_data import load_structured_file
from paperfig.utils.types import FlowTemplate, FlowTemplateCatalog


REQUIRED_TEMPLATE_FIELDS = {
    "id",
    "name",
    "type",
    "inputs",
    "steps",
    "outputs",
    "scoring",
    "metadata",
}


def _resolve_pack_root(template_dir: Path, pack: Optional[str]) -> tuple[Path, str, bool]:
    if pack:
        pack_path = Path(pack)
        if pack_path.exists():
            candidates = [
                pack_path / "templates" / "flows",
                pack_path / "flows",
                pack_path,
            ]
            for candidate in candidates:
                if candidate.is_dir():
                    return candidate, pack_path.name, True

        try:
            has_spec = importlib.util.find_spec(pack) is not None
        except Exception:
            has_spec = False
        if has_spec:
            package_root = resources.files(pack)
            candidates = [
                package_root / "templates" / "flows",
                package_root / "flows",
                package_root,
            ]
            for candidate in candidates:
                if candidate.is_dir():
                    return Path(str(candidate)), pack, True

    return template_dir, "expanded_v1", False


def _normalize_template_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(data)

    if "name" not in normalized and "title" in normalized:
        normalized["name"] = normalized["title"]
    if "type" not in normalized and "kind" in normalized:
        normalized["type"] = normalized["kind"]

    if "inputs" not in normalized and "required_sections" in normalized:
        normalized["inputs"] = {
            "required_sections": normalized.get("required_sections", []),
        }
    if "steps" not in normalized and (
        "trigger_rules" in normalized or "element_blueprint" in normalized
    ):
        normalized["steps"] = [
            {
                "id": "trigger_rules",
                "kind": "trigger",
                "rules": normalized.get("trigger_rules", []),
            },
            {
                "id": "element_blueprint",
                "kind": "structure",
                "blueprint": normalized.get("element_blueprint", {}),
            },
        ]
    if "outputs" not in normalized and (
        "kind" in normalized or "caption_style" in normalized
    ):
        normalized["outputs"] = {
            "figure_kind": normalized.get("kind", normalized.get("type", "unknown")),
            "caption_style": normalized.get("caption_style", "default"),
        }
    if "scoring" not in normalized and "critique_focus" in normalized:
        normalized["scoring"] = {
            "critique_focus": normalized.get("critique_focus", []),
        }
    legacy_metadata_fields = {
        "pack",
        "order_hint",
        "trigger_rules",
        "caption_style",
        "traceability_requirements",
        "critique_focus",
        "required_sections",
        "element_blueprint",
    }
    if "metadata" not in normalized and any(key in normalized for key in legacy_metadata_fields):
        normalized["metadata"] = {
            "pack": normalized.get("pack", "expanded_v1"),
            "order_hint": normalized.get("order_hint", 100),
            "trigger_rules": normalized.get("trigger_rules", []),
            "caption_style": normalized.get("caption_style", "default"),
            "traceability_requirements": normalized.get("traceability_requirements", {}),
            "critique_focus": normalized.get("critique_focus", []),
            "required_sections": normalized.get("required_sections", []),
            "element_blueprint": normalized.get("element_blueprint", {}),
        }

    metadata = normalized.get("metadata", {})
    if isinstance(metadata, dict):
        if "pack" in normalized:
            metadata.setdefault("pack", normalized.get("pack", "expanded_v1"))
        if "order_hint" in normalized:
            metadata.setdefault("order_hint", normalized.get("order_hint", 100))
        if "trigger_rules" in normalized:
            metadata.setdefault("trigger_rules", normalized.get("trigger_rules", []))
        if "caption_style" in normalized:
            metadata.setdefault("caption_style", normalized.get("caption_style", "default"))
        if "traceability_requirements" in normalized:
            metadata.setdefault(
                "traceability_requirements",
                normalized.get("traceability_requirements", {}),
            )
        if "critique_focus" in normalized:
            metadata.setdefault("critique_focus", normalized.get("critique_focus", []))
        if "required_sections" in normalized:
            metadata.setdefault("required_sections", normalized.get("required_sections", []))
        if "element_blueprint" in normalized:
            metadata.setdefault("element_blueprint", normalized.get("element_blueprint", {}))
        normalized["metadata"] = metadata

    return normalized


def _validate_template(data: Dict[str, Any], path: Path) -> None:
    missing = REQUIRED_TEMPLATE_FIELDS - set(data.keys())
    if missing:
        raise RuntimeError(f"Template {path} missing required fields: {sorted(missing)}")


def _to_template(data: Dict[str, Any]) -> FlowTemplate:
    metadata = data.get("metadata", {})
    inputs = data.get("inputs", {})
    scoring = data.get("scoring", {})
    outputs = data.get("outputs", {})
    trigger_rules = metadata.get("trigger_rules", data.get("trigger_rules", []))
    required_sections = metadata.get("required_sections", data.get("required_sections", []))
    element_blueprint = metadata.get("element_blueprint", data.get("element_blueprint", {}))
    caption_style = str(metadata.get("caption_style", data.get("caption_style", "default")))
    traceability_requirements = metadata.get(
        "traceability_requirements",
        data.get("traceability_requirements", {}),
    )
    critique_focus = metadata.get("critique_focus", scoring.get("critique_focus", []))

    return FlowTemplate(
        template_id=str(data["id"]),
        title=str(data.get("title", data["name"])),
        kind=str(data.get("kind", data["type"])),
        order_hint=int(metadata.get("order_hint", data.get("order_hint", 100))),
        required_sections=[str(section) for section in required_sections],
        trigger_rules=[dict(rule) for rule in trigger_rules],
        element_blueprint=dict(element_blueprint),
        caption_style=caption_style,
        traceability_requirements=dict(traceability_requirements),
        critique_focus=[str(item) for item in critique_focus],
        name=str(data["name"]),
        template_type=str(data["type"]),
        inputs=dict(inputs) if isinstance(inputs, dict) else {},
        steps=[dict(step) for step in data.get("steps", []) if isinstance(step, dict)],
        outputs=dict(outputs) if isinstance(outputs, dict) else {},
        scoring=dict(scoring) if isinstance(scoring, dict) else {},
        metadata=dict(metadata) if isinstance(metadata, dict) else {},
    )


def discover_template_files(template_dir: Path, pack: Optional[str] = None) -> tuple[List[Path], str, bool]:
    resolved_dir, resolved_pack_id, is_external_pack = _resolve_pack_root(template_dir, pack)
    if not resolved_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {resolved_dir}")
    return sorted(resolved_dir.glob("*.yaml")), resolved_pack_id, is_external_pack


def load_template_catalog(
    template_dir: Path,
    pack_id: str = "expanded_v1",
    pack: Optional[str] = None,
) -> FlowTemplateCatalog:
    paths, discovered_pack_id, is_external_pack = discover_template_files(template_dir=template_dir, pack=pack)
    if is_external_pack:
        effective_pack_id = discovered_pack_id
    else:
        effective_pack_id = pack_id

    templates: List[FlowTemplate] = []
    for path in paths:
        data = load_structured_file(path)
        if not isinstance(data, dict):
            raise RuntimeError(f"Template file {path} must contain a mapping/object.")

        normalized = _normalize_template_payload(data)
        _validate_template(normalized, path)

        template_pack = str(normalized.get("metadata", {}).get("pack", normalized.get("pack", "expanded_v1")))
        if not is_external_pack and template_pack != effective_pack_id:
            continue
        templates.append(_to_template(normalized))

    return FlowTemplateCatalog(pack_id=effective_pack_id, templates=templates)


def validate_template_catalog(
    template_dir: Path,
    pack_id: str = "expanded_v1",
    pack: Optional[str] = None,
) -> List[str]:
    catalog = load_template_catalog(template_dir=template_dir, pack_id=pack_id, pack=pack)
    errors: List[str] = []

    seen_ids = set()
    for template in catalog.templates:
        if template.template_id in seen_ids:
            errors.append(f"Duplicate template id: {template.template_id}")
        seen_ids.add(template.template_id)

    if not catalog.templates:
        if pack:
            errors.append(f"No templates loaded from pack '{pack}'")
        else:
            errors.append(f"No templates loaded for pack '{pack_id}'")

    return errors
