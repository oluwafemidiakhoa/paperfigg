from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from paperfig.utils.structured_data import load_structured_file
from paperfig.utils.types import FlowTemplate, FlowTemplateCatalog


REQUIRED_TEMPLATE_FIELDS = {
    "id",
    "title",
    "kind",
    "order_hint",
    "required_sections",
    "trigger_rules",
    "element_blueprint",
    "caption_style",
    "traceability_requirements",
    "critique_focus",
}


def _validate_template(data: Dict[str, Any], path: Path) -> None:
    missing = REQUIRED_TEMPLATE_FIELDS - set(data.keys())
    if missing:
        raise RuntimeError(f"Template {path} missing required fields: {sorted(missing)}")


def _to_template(data: Dict[str, Any]) -> FlowTemplate:
    return FlowTemplate(
        template_id=str(data["id"]),
        title=str(data["title"]),
        kind=str(data["kind"]),
        order_hint=int(data["order_hint"]),
        required_sections=[str(section) for section in data.get("required_sections", [])],
        trigger_rules=[dict(rule) for rule in data.get("trigger_rules", [])],
        element_blueprint=dict(data.get("element_blueprint", {})),
        caption_style=str(data.get("caption_style", "default")),
        traceability_requirements=dict(data.get("traceability_requirements", {})),
        critique_focus=[str(item) for item in data.get("critique_focus", [])],
    )


def load_template_catalog(template_dir: Path, pack_id: str = "expanded_v1") -> FlowTemplateCatalog:
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    templates: List[FlowTemplate] = []
    for path in sorted(template_dir.glob("*.yaml")):
        data = load_structured_file(path)
        if not isinstance(data, dict):
            raise RuntimeError(f"Template file {path} must contain a mapping/object.")

        template_pack = str(data.get("pack", "expanded_v1"))
        if template_pack != pack_id:
            continue

        _validate_template(data, path)
        templates.append(_to_template(data))

    return FlowTemplateCatalog(pack_id=pack_id, templates=templates)


def validate_template_catalog(template_dir: Path, pack_id: str = "expanded_v1") -> List[str]:
    catalog = load_template_catalog(template_dir=template_dir, pack_id=pack_id)
    errors: List[str] = []

    seen_ids = set()
    for template in catalog.templates:
        if template.template_id in seen_ids:
            errors.append(f"Duplicate template id: {template.template_id}")
        seen_ids.add(template.template_id)

    if not catalog.templates:
        errors.append(f"No templates loaded for pack '{pack_id}'")

    return errors
