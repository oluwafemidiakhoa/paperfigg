from __future__ import annotations


def propose_hypothesis(topic: str, source_run_id: str = "") -> str:
    if source_run_id:
        return (
            f"Adjust figure planning and critique thresholds for run {source_run_id} "
            "to improve traceability coverage and acceptance rate."
        )
    return f"Investigate whether template-guided generation improves output quality for topic: {topic}."
