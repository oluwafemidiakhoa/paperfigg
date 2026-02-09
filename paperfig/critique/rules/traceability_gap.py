from __future__ import annotations

from typing import List

from paperfig.critique.rules.base import RuleContext
from paperfig.utils.types import ArchitectureCritiqueFinding


RULE_ID = "traceability_gap"
DESCRIPTION = "Detect low traceability coverage across final figures."


def evaluate(context: RuleContext) -> List[ArchitectureCritiqueFinding]:
    if context.inspect_data is None:
        return []

    avg_cov = context.inspect_data.get("aggregate", {}).get("avg_traceability_coverage")
    if not isinstance(avg_cov, (int, float)) or avg_cov >= 0.8:
        return []

    return [
        ArchitectureCritiqueFinding(
            finding_id=RULE_ID,
            severity="major",
            title="Low traceability coverage",
            description="Average traceability coverage is below recommended threshold.",
            evidence=f"avg_traceability_coverage={avg_cov}",
            suggestion="Ensure all figure elements include source span mappings.",
        )
    ]

