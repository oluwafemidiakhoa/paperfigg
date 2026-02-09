from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from paperfig.templates.loader import discover_template_files, _normalize_template_payload
from paperfig.utils.structured_data import load_structured_file


SCHEMA_PATH = Path("paperfig/templates/schema/flow_template.schema.json")


def load_flow_template_schema(schema_path: Path = SCHEMA_PATH) -> Dict[str, Any]:
    if not schema_path.exists():
        raise FileNotFoundError(f"Flow template schema not found: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _simple_schema_validate(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for field in schema.get("required", []):
        if field not in data:
            errors.append(f"{field}: is required")
    return errors


def _jsonschema_validate(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    try:
        from jsonschema import Draft202012Validator
    except Exception:
        return _simple_schema_validate(data, schema)

    validator = Draft202012Validator(schema)
    errors: List[str] = []
    for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
        field = ".".join(str(part) for part in error.path) or "<root>"
        errors.append(f"{field}: {error.message}")
    return errors


def lint_template_catalog(
    template_dir: Path,
    pack: Optional[str] = None,
    schema_path: Path = SCHEMA_PATH,
) -> List[str]:
    schema = load_flow_template_schema(schema_path=schema_path)
    paths, _, _ = discover_template_files(template_dir=template_dir, pack=pack)
    all_errors: List[str] = []
    if not paths:
        source = pack or str(template_dir)
        return [f"{source}: <root>: no template files were found"]

    for path in paths:
        data = load_structured_file(path)
        if not isinstance(data, dict):
            all_errors.append(f"{path}: <root>: template must be a mapping/object")
            continue

        normalized = _normalize_template_payload(data)
        errors = _jsonschema_validate(normalized, schema)
        for error in errors:
            all_errors.append(f"{path}: {error}")

    return all_errors
