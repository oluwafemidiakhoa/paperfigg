from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Set

from paperfig.utils.types import ArchitectureCritiqueFinding


@dataclass
class RuleContext:
    run_dir: Path
    repo_root: Path
    run_metadata: Dict[str, Any]
    inspect_data: Optional[Dict[str, Any]]
    plan_data: Optional[List[Dict[str, Any]]]
    docs_drift_report: Optional[Dict[str, Any]]
    valid_template_ids: Set[str]


RuleEvaluator = Callable[[RuleContext], Sequence[ArchitectureCritiqueFinding]]


@dataclass(frozen=True)
class ArchitectureRule:
    rule_id: str
    description: str
    evaluator: RuleEvaluator

