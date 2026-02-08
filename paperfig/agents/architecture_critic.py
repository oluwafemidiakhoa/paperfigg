from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from paperfig.utils.prompts import load_prompt
from paperfig.utils.types import ArchitectureCritiqueFinding, ArchitectureCritiqueReport


SEVERITY_ORDER = {
    "info": 0,
    "minor": 1,
    "major": 2,
    "critical": 3,
}


class ArchitectureCriticAgent:
    def __init__(self) -> None:
        self.prompt = load_prompt("critique_architecture.txt")

    def critique(self, run_dir: Path, block_severity: str = "critical") -> ArchitectureCritiqueReport:
        run_id = run_dir.name
        findings: List[ArchitectureCritiqueFinding] = []

        inspect_path = run_dir / "inspect.json"
        if not inspect_path.exists():
            findings.append(
                ArchitectureCritiqueFinding(
                    finding_id="missing_inspect",
                    severity="major",
                    title="Missing inspect summary",
                    description="Run is missing inspect.json, limiting architecture observability.",
                    evidence=str(inspect_path),
                    suggestion="Regenerate inspect summary via pipeline finalization or `paperfig inspect`.",
                )
            )
        else:
            inspect_data = json.loads(inspect_path.read_text(encoding="utf-8"))
            failed = inspect_data.get("aggregate", {}).get("failed_count", 0)
            if isinstance(failed, int) and failed > 0:
                findings.append(
                    ArchitectureCritiqueFinding(
                        finding_id="failed_figures",
                        severity="major",
                        title="Failed figures present",
                        description="At least one figure did not pass final critique.",
                        evidence=f"failed_count={failed}",
                        suggestion="Review failed figures and rerun with improved prompts/templates.",
                    )
                )

            avg_cov = inspect_data.get("aggregate", {}).get("avg_traceability_coverage")
            if isinstance(avg_cov, (int, float)) and avg_cov < 0.8:
                findings.append(
                    ArchitectureCritiqueFinding(
                        finding_id="traceability_coverage_low",
                        severity="major",
                        title="Low traceability coverage",
                        description="Average traceability coverage is below recommended threshold.",
                        evidence=f"avg_traceability_coverage={avg_cov}",
                        suggestion="Ensure all figure elements include source span mappings.",
                    )
                )

        plan_path = run_dir / "plan.json"
        if not plan_path.exists():
            findings.append(
                ArchitectureCritiqueFinding(
                    finding_id="missing_plan",
                    severity="critical",
                    title="Missing plan artifact",
                    description="Run is missing plan.json.",
                    evidence=str(plan_path),
                    suggestion="Investigate planner stage and regenerate run artifacts.",
                )
            )
        else:
            plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
            if isinstance(plan_data, list) and not plan_data:
                findings.append(
                    ArchitectureCritiqueFinding(
                        finding_id="empty_plan",
                        severity="critical",
                        title="Empty figure plan",
                        description="Planner generated no figures for this run.",
                        evidence="plan.json contains 0 entries",
                        suggestion="Review section extraction and template trigger rules.",
                    )
                )

        docs_report_path = run_dir / "docs_drift_report.json"
        if not docs_report_path.exists():
            findings.append(
                ArchitectureCritiqueFinding(
                    finding_id="missing_docs_drift_report",
                    severity="minor",
                    title="Missing docs drift report",
                    description="No docs_drift_report.json was found for this run.",
                    evidence=str(docs_report_path),
                    suggestion="Enable docs check in the generation finalization stage.",
                )
            )

        max_seen = max((SEVERITY_ORDER.get(item.severity, 0) for item in findings), default=0)
        blocked = max_seen >= SEVERITY_ORDER.get(block_severity, SEVERITY_ORDER["critical"])

        summary = "No architecture findings."
        if findings:
            summary = f"{len(findings)} finding(s); highest severity={self._severity_name(max_seen)}"

        return ArchitectureCritiqueReport(
            run_id=run_id,
            block_severity=block_severity,
            findings=findings,
            blocked=blocked,
            summary=summary,
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    @staticmethod
    def _severity_name(value: int) -> str:
        for name, rank in SEVERITY_ORDER.items():
            if rank == value:
                return name
        return "info"


def report_to_dict(report: ArchitectureCritiqueReport) -> Dict[str, object]:
    return asdict(report)
