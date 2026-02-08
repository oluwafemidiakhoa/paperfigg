from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class LabPolicy:
    allowed_prefixes: List[str] = field(default_factory=list)
    blocked_patterns: List[str] = field(default_factory=list)
    max_runtime_seconds: int = 1200
    max_parallel_experiments: int = 1


@dataclass
class LabExperimentSpec:
    experiment_id: str
    topic: str
    source_run_id: str
    hypothesis: str
    command: str
    status: str = "proposed"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LabExperimentResult:
    experiment_id: str
    status: str
    return_code: int
    started_at: str
    finished_at: str
    stdout: str
    stderr: str
    policy_violation: str = ""
