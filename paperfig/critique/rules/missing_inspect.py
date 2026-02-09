from __future__ import annotations

from typing import List

from paperfig.critique.rules.base import RuleContext
from paperfig.utils.types import ArchitectureCritiqueFinding


RULE_ID = "missing_inspect"
DESCRIPTION = "Require inspect.json so architecture quality can be assessed."


def evaluate(context: RuleContext) -> List[ArchitectureCritiqueFinding]:
    if context.inspect_data is not None:
        return []
    return [
        ArchitectureCritiqueFinding(
            finding_id=RULE_ID,
            severity="major",
            title="Missing inspect summary",
            description="Run is missing inspect.json, limiting architecture observability.",
            evidence=str(context.run_dir / "inspect.json"),
            suggestion="Regenerate inspect summary via pipeline finalization or `paperfig inspect`.",
        )
    ]

