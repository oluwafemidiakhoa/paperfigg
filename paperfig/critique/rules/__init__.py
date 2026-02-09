from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from . import (
    empty_plan,
    failed_figures,
    invalid_template_reference,
    missing_docs_drift_report,
    missing_flow_docs,
    missing_inspect,
    missing_plan,
    traceability_gap,
)
from .base import ArchitectureRule


def get_rule_registry() -> Dict[str, ArchitectureRule]:
    rules = [
        ArchitectureRule(
            rule_id=missing_inspect.RULE_ID,
            description=missing_inspect.DESCRIPTION,
            evaluator=missing_inspect.evaluate,
        ),
        ArchitectureRule(
            rule_id=failed_figures.RULE_ID,
            description=failed_figures.DESCRIPTION,
            evaluator=failed_figures.evaluate,
        ),
        ArchitectureRule(
            rule_id=traceability_gap.RULE_ID,
            description=traceability_gap.DESCRIPTION,
            evaluator=traceability_gap.evaluate,
        ),
        ArchitectureRule(
            rule_id=missing_plan.RULE_ID,
            description=missing_plan.DESCRIPTION,
            evaluator=missing_plan.evaluate,
        ),
        ArchitectureRule(
            rule_id=empty_plan.RULE_ID,
            description=empty_plan.DESCRIPTION,
            evaluator=empty_plan.evaluate,
        ),
        ArchitectureRule(
            rule_id=missing_docs_drift_report.RULE_ID,
            description=missing_docs_drift_report.DESCRIPTION,
            evaluator=missing_docs_drift_report.evaluate,
        ),
        ArchitectureRule(
            rule_id=missing_flow_docs.RULE_ID,
            description=missing_flow_docs.DESCRIPTION,
            evaluator=missing_flow_docs.evaluate,
        ),
        ArchitectureRule(
            rule_id=invalid_template_reference.RULE_ID,
            description=invalid_template_reference.DESCRIPTION,
            evaluator=invalid_template_reference.evaluate,
        ),
    ]
    return {rule.rule_id: rule for rule in rules}


def list_rule_descriptors() -> List[dict]:
    registry = get_rule_registry()
    return [
        {"rule_id": rule_id, "description": rule.description}
        for rule_id, rule in sorted(registry.items())
    ]


def resolve_enabled_rules(enable: Optional[Iterable[str]]) -> List[ArchitectureRule]:
    registry = get_rule_registry()
    if not enable:
        return [registry[key] for key in sorted(registry.keys())]

    selected: List[ArchitectureRule] = []
    for rule_id in enable:
        if rule_id not in registry:
            available = ", ".join(sorted(registry.keys()))
            raise ValueError(f"Unknown architecture rule '{rule_id}'. Available: {available}")
        selected.append(registry[rule_id])
    return selected
