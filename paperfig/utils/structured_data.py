from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_structured_file(path: Path) -> Any:
    raw = path.read_text(encoding="utf-8")

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    try:
        import yaml  # type: ignore

        return yaml.safe_load(raw)
    except Exception as exc:
        raise RuntimeError(
            f"Unable to parse structured file {path}. "
            "Provide JSON content or install PyYAML for full YAML support."
        ) from exc


def dump_structured_data(data: Any, as_yaml: bool = True) -> str:
    if as_yaml:
        try:
            import yaml  # type: ignore

            return yaml.safe_dump(data, sort_keys=False)
        except Exception:
            pass
    return json.dumps(data, indent=2)
