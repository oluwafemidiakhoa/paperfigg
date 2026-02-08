from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from paperfig.lab.orchestrator import LabOrchestrator
from paperfig.lab.policy import is_command_allowed, load_policy
from paperfig.utils.structured_data import dump_structured_data, load_structured_file


class LabTests(unittest.TestCase):
    def _write_policy(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "allowed_prefixes": ["python3", "echo"],
                    "blocked_patterns": ["rm -rf", "git reset --hard"],
                    "max_runtime_seconds": 60,
                    "max_parallel_experiments": 1,
                }
            ),
            encoding="utf-8",
        )

    def test_policy_blocks_forbidden_patterns(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            policy_path = Path(tmpdir) / "policy.yaml"
            self._write_policy(policy_path)
            policy = load_policy(policy_path)

            allowed, reason = is_command_allowed("python3 -c 'print(1)'", policy)
            self.assertTrue(allowed)
            self.assertEqual(reason, "allowed")

            blocked, reason = is_command_allowed("python3 -c 'print(1)' && rm -rf /tmp/x", policy)
            self.assertFalse(blocked)
            self.assertIn("blocked", reason.lower())

    def test_lab_orchestrator_propose_run_review_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            policy_path = root / "config" / "lab_policy.yaml"
            self._write_policy(policy_path)

            orchestrator = LabOrchestrator(
                root_dir=root / "lab_runs",
                policy_path=policy_path,
                runs_root=root / "runs",
            )

            lab_run_id = orchestrator.init_lab()
            self.assertTrue((root / "lab_runs" / lab_run_id).exists())

            spec = orchestrator.propose("template quality exploration", lab_run_id=lab_run_id)
            exp_dir = root / "lab_runs" / lab_run_id / "experiments" / spec.experiment_id
            self.assertTrue((exp_dir / "spec.yaml").exists())

            # Replace default command to keep the test short and deterministic.
            spec_data = load_structured_file(exp_dir / "spec.yaml")
            spec_data["command"] = "python3 -c \"print('lab-ok')\""
            (exp_dir / "spec.yaml").write_text(dump_structured_data(spec_data, as_yaml=True), encoding="utf-8")

            result = orchestrator.run(spec.experiment_id, lab_run_id=lab_run_id)
            self.assertEqual(result.status, "completed")
            self.assertEqual(result.return_code, 0)
            self.assertTrue((exp_dir / "execution_log.json").exists())

            review = orchestrator.review(spec.experiment_id, lab_run_id=lab_run_id)
            self.assertIn("recommendation", review)
            self.assertTrue((exp_dir / "review.json").exists())

            status = orchestrator.status(lab_run_id=lab_run_id)
            self.assertEqual(status["lab_run_id"], lab_run_id)
            self.assertGreaterEqual(len(status["experiments"]), 1)


if __name__ == "__main__":
    unittest.main()
