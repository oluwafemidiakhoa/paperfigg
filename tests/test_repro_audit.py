from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from paperfig.audits.reproducibility import run_reproducibility_audit
from paperfig.utils.config import config_hash, load_config


class ReproAuditTests(unittest.TestCase):
    def _build_complete_run(self, run_dir: Path) -> None:
        run_dir.mkdir(parents=True, exist_ok=True)
        cfg_hash = config_hash(load_config(Path("paperfig.yaml")))
        (run_dir / "run.json").write_text(
            json.dumps(
                {
                    "run_id": run_dir.name,
                    "paper_path": "examples/sample_paper.md",
                    "created_at": "2026-02-08T00:00:00Z",
                    "config_hash": cfg_hash,
                }
            ),
            encoding="utf-8",
        )
        for rel in [
            "plan.json",
            "sections.json",
            "traceability.json",
            "inspect.json",
            "docs_drift_report.json",
            "architecture_critique.json",
            "prompts/plan_figure.txt",
            "prompts/critique_figure.txt",
        ]:
            path = run_dir / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}", encoding="utf-8")

    def test_repro_audit_passes_when_artifacts_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "run-a"
            self._build_complete_run(run_dir)
            cfg_hash = config_hash(load_config(Path("paperfig.yaml")))

            report = run_reproducibility_audit(run_dir, mode="soft", expected_config_hash=cfg_hash)
            self.assertTrue(report.passed)
            self.assertEqual(report.mode, "soft")

    def test_repro_audit_fails_when_required_artifact_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "run-b"
            self._build_complete_run(run_dir)
            (run_dir / "inspect.json").unlink()

            report = run_reproducibility_audit(run_dir, mode="hard")
            self.assertFalse(report.passed)
            failed_required = [check for check in report.checks if check.required and not check.passed]
            self.assertGreaterEqual(len(failed_required), 1)


if __name__ == "__main__":
    unittest.main()
