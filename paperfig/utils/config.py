from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from .structured_data import load_structured_file

DEFAULT_CONFIG: Dict[str, Any] = {
    "docs": {
        "scope": "all",
        "manifest_path": "docs/docs_manifest.yaml",
        "auto_regen_on_generate": True,
    },
    "architecture_critique": {
        "inline_on_generate": True,
        "block_severity": "critical",
        "output_file": "architecture_critique.json",
    },
    "reproducibility": {
        "mode": "soft",
        "output_file": "repro_audit.json",
    },
    "templates": {
        "active_pack": "expanded_v1",
        "template_dir": "paperfig/templates/flows",
    },
    "lab": {
        "runtime": "single_node_local",
        "sandbox_policy": "config/lab_policy.yaml",
        "registry_dir": "lab_runs",
    },
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config_path: Path = Path("paperfig.yaml")) -> Dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    if config_path.exists():
        user_config = load_structured_file(config_path)
        if not isinstance(user_config, dict):
            raise RuntimeError(f"Config file {config_path} must contain a mapping/object.")
        config = _deep_merge(config, user_config)
    return config


def config_hash(config: Dict[str, Any]) -> str:
    canonical = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
