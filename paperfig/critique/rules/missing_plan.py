from __future__ import annotations

from typing import List

from paperfig.critique.rules.base import RuleContext
from paperfig.utils.types import ArchitectureCritiqueFinding


RULE_ID = "missing_plan"
DESCRIPTION = "Require run plan artifact."


def evaluate(context: RuleContext) -> List[ArchitectureCritiqueFinding]:
    if context.plan_data is not None:
        return []
    return [
        ArchitectureCritiqueFinding(
            finding_id=RULE_ID,
            severity="critical",
            title="Missing plan artifact",
            description="Run is missing plan.json.",
            evidence=str(context.run_dir / "plan.json"),
            suggestion="Investigate planner stage and regenerate run artifacts.",
        )
    ]

