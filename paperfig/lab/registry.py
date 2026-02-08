from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict


def init_registry(registry_dir: Path) -> None:
    registry_dir.mkdir(parents=True, exist_ok=True)
    index_path = registry_dir / "index.json"
    if not index_path.exists():
        index = {
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "experiments": {},
        }
        index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")


def load_index(registry_dir: Path) -> Dict[str, Any]:
    index_path = registry_dir / "index.json"
    if not index_path.exists():
        init_registry(registry_dir)
    return json.loads(index_path.read_text(encoding="utf-8"))


def save_index(registry_dir: Path, index: Dict[str, Any]) -> None:
    index_path = registry_dir / "index.json"
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")


def upsert_experiment(registry_dir: Path, experiment_id: str, payload: Dict[str, Any]) -> None:
    index = load_index(registry_dir)
    experiments = index.setdefault("experiments", {})
    experiments[experiment_id] = payload
    save_index(registry_dir, index)
