from __future__ import annotations

from typing import List

from paperfig.critique.rules.base import RuleContext
from paperfig.utils.types import ArchitectureCritiqueFinding


RULE_ID = "missing_docs_drift_report"
DESCRIPTION = "Require docs drift report artifact for governance traceability."


def evaluate(context: RuleContext) -> List[ArchitectureCritiqueFinding]:
    if context.docs_drift_report is not None:
        return []
    return [
        ArchitectureCritiqueFinding(
            finding_id=RULE_ID,
            severity="minor",
            title="Missing docs drift report",
            description="No docs_drift_report.json was found for this run.",
            evidence=str(context.run_dir / "docs_drift_report.json"),
            suggestion="Enable docs check in the generation finalization stage.",
        )
    ]

