from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from paperfig.audits.reproducibility import report_to_dict, run_reproducibility_audit
from paperfig.lab.agents.designer import design_experiment_command
from paperfig.lab.agents.executor import execute_command
from paperfig.lab.agents.hypothesis import propose_hypothesis
from paperfig.lab.agents.reviewer import review_experiment
from paperfig.lab.policy import load_policy
from paperfig.lab.registry import init_registry, load_index, save_index, upsert_experiment
from paperfig.lab.types import LabExperimentResult, LabExperimentSpec
from paperfig.utils.structured_data import dump_structured_data, load_structured_file


class LabOrchestrator:
    def __init__(self, root_dir: Path, policy_path: Path, runs_root: Path = Path("runs")) -> None:
        self.root_dir = root_dir
        self.policy_path = policy_path
        self.runs_root = runs_root

    def init_lab(self) -> str:
        self.root_dir.mkdir(parents=True, exist_ok=True)
        lab_run_id = f"lab-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        lab_dir = self.root_dir / lab_run_id
        (lab_dir / "experiments").mkdir(parents=True, exist_ok=True)
        init_registry(lab_dir)
        (self.root_dir / "current.txt").write_text(lab_run_id, encoding="utf-8")
        return lab_run_id

    def resolve_lab_run(self, lab_run_id: Optional[str] = None) -> Tuple[str, Path]:
        if lab_run_id:
            run_dir = self.root_dir / lab_run_id
            if not run_dir.exists():
                raise FileNotFoundError(f"Lab run not found: {lab_run_id}")
            return lab_run_id, run_dir

        current = self.root_dir / "current.txt"
        if current.exists():
            current_id = current.read_text(encoding="utf-8").strip()
            run_dir = self.root_dir / current_id
            if run_dir.exists():
                return current_id, run_dir

        created = self.init_lab()
        return created, self.root_dir / created

    def propose(self, topic_or_run_id: str, lab_run_id: Optional[str] = None) -> LabExperimentSpec:
        run_id, run_dir = self.resolve_lab_run(lab_run_id)
        experiments_dir = run_dir / "experiments"
        experiments_dir.mkdir(parents=True, exist_ok=True)

        source_run_id = ""
        if (self.runs_root / topic_or_run_id).exists():
            source_run_id = topic_or_run_id

        topic = topic_or_run_id
        hypothesis = propose_hypothesis(topic, source_run_id=source_run_id)
        command = design_experiment_command(topic, source_run_id=source_run_id)

        experiment_id = f"exp-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
        spec = LabExperimentSpec(
            experiment_id=experiment_id,
            topic=topic,
            source_run_id=source_run_id,
            hypothesis=hypothesis,
            command=command,
            status="proposed",
            metadata={
                "lab_run_id": run_id,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        )

        exp_dir = experiments_dir / experiment_id
        exp_dir.mkdir(parents=True, exist_ok=True)
        (exp_dir / "spec.yaml").write_text(dump_structured_data(asdict(spec), as_yaml=True), encoding="utf-8")

        upsert_experiment(run_dir, experiment_id, {
            "experiment_id": experiment_id,
            "status": "proposed",
            "source_run_id": source_run_id,
            "topic": topic,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })

        return spec

    def run(self, experiment_id: str, lab_run_id: Optional[str] = None) -> LabExperimentResult:
        _, run_dir = self.resolve_lab_run(lab_run_id)
        exp_dir = run_dir / "experiments" / experiment_id
        spec_path = exp_dir / "spec.yaml"
        if not spec_path.exists():
            raise FileNotFoundError(f"Experiment spec not found: {spec_path}")

        spec_data = load_structured_file(spec_path)
        spec = LabExperimentSpec(**spec_data)

        policy = load_policy(self.policy_path)
        result = execute_command(spec.command, policy)
        result.experiment_id = experiment_id

        (exp_dir / "execution_log.json").write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")

        spec.status = "completed" if result.status == "completed" else "failed"
        (exp_dir / "spec.yaml").write_text(dump_structured_data(asdict(spec), as_yaml=True), encoding="utf-8")

        upsert_experiment(run_dir, experiment_id, {
            "experiment_id": experiment_id,
            "status": spec.status,
            "source_run_id": spec.source_run_id,
            "topic": spec.topic,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })

        return result

    def review(self, experiment_id: str, lab_run_id: Optional[str] = None) -> Dict[str, object]:
        _, run_dir = self.resolve_lab_run(lab_run_id)
        exp_dir = run_dir / "experiments" / experiment_id
        spec_path = exp_dir / "spec.yaml"
        execution_path = exp_dir / "execution_log.json"

        if not spec_path.exists() or not execution_path.exists():
            raise FileNotFoundError("Experiment spec or execution log missing for review.")

        spec_data = load_structured_file(spec_path)
        spec = LabExperimentSpec(**spec_data)
        result_data = json.loads(execution_path.read_text(encoding="utf-8"))
        result = LabExperimentResult(**result_data)

        review = review_experiment(spec, result)

        if spec.source_run_id and (self.runs_root / spec.source_run_id).exists():
            audit_report = run_reproducibility_audit(self.runs_root / spec.source_run_id, mode="soft")
            review["repro_audit"] = report_to_dict(audit_report)

        (exp_dir / "review.json").write_text(json.dumps(review, indent=2), encoding="utf-8")

        upsert_experiment(run_dir, experiment_id, {
            "experiment_id": experiment_id,
            "status": "reviewed",
            "source_run_id": spec.source_run_id,
            "topic": spec.topic,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })

        return review

    def status(self, lab_run_id: Optional[str] = None) -> Dict[str, object]:
        run_id, run_dir = self.resolve_lab_run(lab_run_id)
        index = load_index(run_dir)

        experiments = list(index.get("experiments", {}).values())
        counts = {
            "proposed": sum(1 for item in experiments if item.get("status") == "proposed"),
            "completed": sum(1 for item in experiments if item.get("status") == "completed"),
            "failed": sum(1 for item in experiments if item.get("status") == "failed"),
            "reviewed": sum(1 for item in experiments if item.get("status") == "reviewed"),
        }

        return {
            "lab_run_id": run_id,
            "counts": counts,
            "experiments": experiments,
        }
