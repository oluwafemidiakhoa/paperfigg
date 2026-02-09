from __future__ import annotations

from typing import List

from paperfig.critique.rules.base import RuleContext
from paperfig.utils.types import ArchitectureCritiqueFinding


RULE_ID = "missing_flow_docs"
DESCRIPTION = "Verify every architecture flow folder contains README.md and diagram.mermaid."


def evaluate(context: RuleContext) -> List[ArchitectureCritiqueFinding]:
    flows_root = context.repo_root / "docs" / "architecture" / "flows"
    if not flows_root.exists():
        return [
            ArchitectureCritiqueFinding(
                finding_id=RULE_ID,
                severity="major",
                title="Missing architecture flows directory",
                description="Architecture flow documentation directory is missing.",
                evidence=str(flows_root),
                suggestion="Restore docs/architecture/flows with README and Mermaid diagrams.",
            )
        ]

    missing_artifacts: List[str] = []
    for subdir in sorted(flows_root.iterdir()):
        if not subdir.is_dir():
            continue
        readme = subdir / "README.md"
        diagram = subdir / "diagram.mermaid"
        if not readme.exists() or not diagram.exists():
            missing_parts = []
            if not readme.exists():
                missing_parts.append("README.md")
            if not diagram.exists():
                missing_parts.append("diagram.mermaid")
            missing_artifacts.append(f"{subdir.name}: {', '.join(missing_parts)}")

    if not missing_artifacts:
        return []

    return [
        ArchitectureCritiqueFinding(
            finding_id=RULE_ID,
            severity="minor",
            title="Incomplete architecture flow docs",
            description="One or more flow folders are missing required documentation files.",
            evidence="; ".join(missing_artifacts),
            suggestion="Add missing README.md and diagram.mermaid for each flow folder.",
        )
    ]

