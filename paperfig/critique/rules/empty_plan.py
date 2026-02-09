from __future__ import annotations

from typing import List

from paperfig.critique.rules.base import RuleContext
from paperfig.utils.types import ArchitectureCritiqueFinding


RULE_ID = "empty_plan"
DESCRIPTION = "Reject runs where planner emitted no figure plans."


def evaluate(context: RuleContext) -> List[ArchitectureCritiqueFinding]:
    if context.plan_data is None:
        return []
    if context.plan_data:
        return []
    return [
        ArchitectureCritiqueFinding(
            finding_id=RULE_ID,
            severity="critical",
            title="Empty figure plan",
            description="Planner generated no figures for this run.",
            evidence="plan.json contains 0 entries",
            suggestion="Review section extraction and template trigger rules.",
        )
    ]

