from __future__ import annotations

from typing import List

from paperfig.critique.rules.base import RuleContext
from paperfig.utils.types import ArchitectureCritiqueFinding


RULE_ID = "invalid_template_reference"
DESCRIPTION = "Ensure plan template IDs exist in the active template catalog."

_ALLOWED_SPECIAL_TEMPLATE_IDS = {"heuristic_fallback", "manual", ""}


def evaluate(context: RuleContext) -> List[ArchitectureCritiqueFinding]:
    if not context.plan_data or not context.valid_template_ids:
        return []

    invalid = []
    for entry in context.plan_data:
        template_id = str(entry.get("template_id", ""))
        if template_id in _ALLOWED_SPECIAL_TEMPLATE_IDS:
            continue
        if template_id not in context.valid_template_ids:
            invalid.append(template_id)

    if not invalid:
        return []

    unique_invalid = sorted(set(invalid))
    return [
        ArchitectureCritiqueFinding(
            finding_id=RULE_ID,
            severity="major",
            title="Invalid template references in plan",
            description="One or more plan entries reference unknown templates.",
            evidence=", ".join(unique_invalid),
            suggestion="Fix template IDs or point generation to the correct template pack.",
        )
    ]

