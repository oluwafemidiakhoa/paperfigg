from __future__ import annotations

import json
import platform
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Tuple

from paperfig.utils.types import ReproAuditCheck, ReproAuditReport


def _artifact_check(run_dir: Path, relative_path: str, required: bool = True) -> ReproAuditCheck:
    path = run_dir / relative_path
    exists = path.exists()
    return ReproAuditCheck(
        check_id=f"artifact_{relative_path.replace('/', '_')}",
        description=f"Artifact exists: {relative_path}",
        required=required,
        passed=exists,
        severity="major" if required else "minor",
        message="present" if exists else "missing",
        details={"path": str(path)},
    )


def _load_run_json(run_dir: Path) -> Tuple[Dict[str, object], bool]:
    run_json_path = run_dir / "run.json"
    if not run_json_path.exists():
        return {}, False
    return json.loads(run_json_path.read_text(encoding="utf-8")), True


def run_reproducibility_audit(
    run_dir: Path,
    mode: str = "soft",
    expected_config_hash: str | None = None,
) -> ReproAuditReport:
    run_id = run_dir.name
    checks: List[ReproAuditCheck] = []

    run_json, has_run_json = _load_run_json(run_dir)
    checks.append(
        ReproAuditCheck(
            check_id="run_json_present",
            description="Run metadata file exists",
            required=True,
            passed=has_run_json,
            severity="critical",
            message="present" if has_run_json else "missing",
            details={"path": str(run_dir / "run.json")},
        )
    )

    checks.extend(
        [
            _artifact_check(run_dir, "plan.json", required=True),
            _artifact_check(run_dir, "sections.json", required=True),
            _artifact_check(run_dir, "traceability.json", required=True),
            _artifact_check(run_dir, "inspect.json", required=True),
            _artifact_check(run_dir, "docs_drift_report.json", required=True),
            _artifact_check(run_dir, "architecture_critique.json", required=True),
            _artifact_check(run_dir, "prompts/plan_figure.txt", required=True),
            _artifact_check(run_dir, "prompts/critique_figure.txt", required=True),
        ]
    )

    has_command_meta = bool(run_json.get("paper_path")) and bool(run_json.get("created_at"))
    checks.append(
        ReproAuditCheck(
            check_id="provenance_metadata",
            description="Run metadata captures provenance fields",
            required=True,
            passed=has_command_meta,
            severity="major",
            message="ok" if has_command_meta else "missing_fields",
            details={"required_fields": ["paper_path", "created_at"]},
        )
    )

    has_seed = "seed" in run_json
    checks.append(
        ReproAuditCheck(
            check_id="deterministic_seed_declared",
            description="Run metadata declares a deterministic seed",
            required=False,
            passed=has_seed,
            severity="minor",
            message="seed_present" if has_seed else "seed_missing",
            details={},
        )
    )

    if expected_config_hash:
        run_hash = str(run_json.get("config_hash", ""))
        checks.append(
            ReproAuditCheck(
                check_id="config_hash_match",
                description="Run metadata config hash matches expected hash",
                required=True,
                passed=(run_hash == expected_config_hash),
                severity="major",
                message="match" if run_hash == expected_config_hash else "mismatch",
                details={"expected": expected_config_hash, "actual": run_hash},
            )
        )

    required_failed = [check for check in checks if check.required and not check.passed]
    passed = len(required_failed) == 0

    summary = "Reproducibility checks passed."
    if not passed:
        summary = f"{len(required_failed)} required reproducibility check(s) failed."

    return ReproAuditReport(
        run_id=run_id,
        mode=mode,
        checks=checks,
        passed=passed,
        summary=summary,
        generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        environment={
            "python_version": sys.version,
            "platform": platform.platform(),
        },
    )


def report_to_dict(report: ReproAuditReport) -> Dict[str, object]:
    return asdict(report)
