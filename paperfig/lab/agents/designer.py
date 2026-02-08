from __future__ import annotations


def design_experiment_command(topic: str, source_run_id: str = "") -> str:
    del topic
    if source_run_id:
        return "python3 -m paperfig.cli inspect " + source_run_id + " --as-json"
    return "python3 -m unittest discover -s tests -v"
