from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from paperfig.utils.paperbanana import PaperBananaClient
from paperfig.utils.traceability import build_traceability, write_traceability
from paperfig.utils.types import FigureCandidate, FigurePlan, PaperContent


class GeneratorAgent:
    def __init__(self, paperbanana_client: Optional[PaperBananaClient] = None) -> None:
        self.paperbanana = paperbanana_client or PaperBananaClient()

    def generate(
        self,
        plan: FigurePlan,
        paper: PaperContent,
        output_dir: Path,
        iteration: int,
        style_refs: Optional[Dict[str, Any]] = None,
        critique_feedback: Optional[Dict[str, Any]] = None,
    ) -> FigureCandidate:
        output_dir.mkdir(parents=True, exist_ok=True)
        svg_path = output_dir / "figure.svg"
        element_metadata_path = output_dir / "element_metadata.json"
        traceability_path = output_dir / "traceability.json"

        spec = {
            "figure_id": plan.figure_id,
            "title": plan.title,
            "kind": plan.kind,
            "description": plan.description,
            "abstraction_level": plan.abstraction_level,
            "source_text": {
                "methodology": paper.sections.get("methodology").text if paper.sections.get("methodology") else "",
                "system": paper.sections.get("system").text if paper.sections.get("system") else "",
                "results": paper.sections.get("results").text if paper.sections.get("results") else "",
            },
            "source_spans": plan.source_spans,
            "style_refs": style_refs or {},
            "critique_feedback": critique_feedback or {},
            "iteration": iteration,
        }

        spec_path = output_dir / "spec.json"
        with open(spec_path, "w", encoding="utf-8") as handle:
            json.dump(spec, handle, indent=2)

        svg, elements = self.paperbanana.generate_svg(spec)
        svg_path.write_text(svg, encoding="utf-8")

        if not elements:
            elements = [
                {
                    "id": f"{plan.figure_id}-summary",
                    "type": "group",
                    "label": plan.title,
                    "source_spans": plan.source_spans,
                }
            ]

        with open(element_metadata_path, "w", encoding="utf-8") as handle:
            json.dump(elements, handle, indent=2)

        traceability = build_traceability(plan.figure_id, elements)
        write_traceability(str(traceability_path), traceability)

        return FigureCandidate(
            figure_id=plan.figure_id,
            svg_path=str(svg_path),
            element_metadata_path=str(element_metadata_path),
            traceability_path=str(traceability_path),
        )
