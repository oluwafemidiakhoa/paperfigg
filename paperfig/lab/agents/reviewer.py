from __future__ import annotations

from typing import Dict

from paperfig.lab.types import LabExperimentResult, LabExperimentSpec


def review_experiment(spec: LabExperimentSpec, result: LabExperimentResult) -> Dict[str, object]:
    recommendation = "revise"
    rationale = "Execution failed or produced policy violations."

    if result.status == "completed" and result.return_code == 0 and not result.policy_violation:
        recommendation = "promote"
        rationale = "Execution completed successfully and respected sandbox policy."

    return {
        "experiment_id": spec.experiment_id,
        "recommendation": recommendation,
        "rationale": rationale,
        "status": result.status,
        "return_code": result.return_code,
        "policy_violation": result.policy_violation,
    }
