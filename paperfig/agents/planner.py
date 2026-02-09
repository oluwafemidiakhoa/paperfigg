from __future__ import annotations

import uuid
from pathlib import Path
from typing import List

from paperfig.templates.compiler import select_templates
from paperfig.templates.loader import load_template_catalog
from paperfig.utils.prompts import load_prompt
from paperfig.utils.types import FigurePlan, PaperContent


class PlannerAgent:
    def __init__(self, template_dir: Path | None = None, template_pack: str = "expanded_v1") -> None:
        self.prompt = load_prompt("plan_figure.txt")
        self.template_dir = template_dir or Path("paperfig/templates/flows")
        self.template_pack = template_pack

    def plan(self, paper: PaperContent) -> List[FigurePlan]:
        template_plans = self._plan_from_templates(paper)
        if template_plans:
            return template_plans

        # Heuristic fallback when templates are unavailable or no template matched.
        plans: List[FigurePlan] = []
        order = 1

        def _add(kind: str, title: str, description: str, justification: str, section_name: str) -> None:
            nonlocal order
            section = paper.sections.get(section_name)
            spans = []
            if section and section.text:
                spans.append(
                    {
                        "section": section.name,
                        "start": section.start,
                        "end": section.end,
                        "quote": section.text[:300].strip(),
                    }
                )
            plans.append(
                FigurePlan(
                    figure_id=f"fig-{uuid.uuid4().hex[:8]}",
                    title=title,
                    kind=kind,
                    order=order,
                    abstraction_level="high" if kind in {"system_overview", "methodology"} else "medium",
                    description=description,
                    justification=justification,
                    template_id="heuristic_fallback",
                    source_spans=spans,
                )
            )
            order += 1

        if paper.sections.get("methodology") and paper.sections["methodology"].text:
            _add(
                kind="methodology",
                title="Methodology Diagram",
                description="Pipeline-level depiction of the proposed methodology and major components.",
                justification="The paper describes a step-by-step methodology that benefits from a flow diagram.",
                section_name="methodology",
            )

        if paper.sections.get("system") and paper.sections["system"].text:
            _add(
                kind="system_overview",
                title="System Overview",
                description="Architecture-level system overview showing modules and data flow.",
                justification="The system description introduces modules and their interactions that should be visualized.",
                section_name="system",
            )

        if paper.sections.get("results") and paper.sections["results"].text:
            _add(
                kind="results_plot",
                title="Results Summary",
                description="Key quantitative results plotted for comparison.",
                justification="The results section summarizes experiments that should be shown as a plot or table.",
                section_name="results",
            )

        if not plans:
            _add(
                kind="summary",
                title="Paper Summary",
                description="High-level overview figure summarizing the main contribution.",
                justification="No explicit sections were detected; provide a summary-level figure.",
                section_name="methodology",
            )

        return plans

    def _plan_from_templates(self, paper: PaperContent) -> List[FigurePlan]:
        try:
            catalog = load_template_catalog(
                template_dir=self.template_dir,
                pack_id=self.template_pack,
                pack=self.template_pack,
            )
        except Exception:
            return []

        selected = select_templates(catalog.templates, paper)
        plans: List[FigurePlan] = []

        for idx, template in enumerate(selected, start=1):
            spans = []
            for section_name in template.required_sections:
                section = paper.sections.get(section_name)
                if section and section.text:
                    spans.append(
                        {
                            "section": section.name,
                            "start": section.start,
                            "end": section.end,
                            "quote": section.text[:300].strip(),
                        }
                    )

            plans.append(
                FigurePlan(
                    figure_id=f"fig-{uuid.uuid4().hex[:8]}",
                    title=template.title,
                    kind=template.kind,
                    order=idx,
                    abstraction_level="high" if template.kind in {"system_overview", "methodology"} else "medium",
                    description=f"Template-driven figure using {template.template_id}.",
                    justification=(
                        f"Selected by template '{template.template_id}' based on required sections "
                        f"and trigger rules."
                    ),
                    template_id=template.template_id,
                    source_spans=spans,
                )
            )

        return plans
