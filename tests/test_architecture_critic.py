from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from paperfig.agents.architecture_critic import ArchitectureCriticAgent


class ArchitectureCriticTests(unittest.TestCase):
    def test_missing_plan_is_critical_and_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "run-x"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "inspect.json").write_text(
                json.dumps({"aggregate": {"failed_count": 0, "avg_traceability_coverage": 1.0}}),
                encoding="utf-8",
            )

            report = ArchitectureCriticAgent().critique(run_dir, block_severity="critical")
            self.assertTrue(report.blocked)
            ids = {item.finding_id for item in report.findings}
            self.assertIn("missing_plan", ids)

    def test_non_blocking_findings_when_only_minor_issues_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "run-y"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "plan.json").write_text(
                json.dumps([{"figure_id": "fig-a"}]),
                encoding="utf-8",
            )
            (run_dir / "inspect.json").write_text(
                json.dumps({"aggregate": {"failed_count": 0, "avg_traceability_coverage": 0.9}}),
                encoding="utf-8",
            )

            report = ArchitectureCriticAgent().critique(run_dir, block_severity="critical")
            self.assertFalse(report.blocked)
            severities = {item.severity for item in report.findings}
            self.assertIn("minor", severities)


if __name__ == "__main__":
    unittest.main()
