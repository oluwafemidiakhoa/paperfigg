from __future__ import annotations

from typing import List

from paperfig.critique.rules.base import RuleContext
from paperfig.utils.types import ArchitectureCritiqueFinding


RULE_ID = "failed_figures"
DESCRIPTION = "Flag runs where one or more figures fail final critique."


def evaluate(context: RuleContext) -> List[ArchitectureCritiqueFinding]:
    if context.inspect_data is None:
        return []

    failed = context.inspect_data.get("aggregate", {}).get("failed_count", 0)
    if not isinstance(failed, int) or failed <= 0:
        return []

    return [
        ArchitectureCritiqueFinding(
            finding_id=RULE_ID,
            severity="major",
            title="Failed figures present",
            description="At least one figure did not pass final critique.",
            evidence=f"failed_count={failed}",
            suggestion="Review failed figures and rerun with improved prompts/templates.",
        )
    ]

