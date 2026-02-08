from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from paperfig.utils.prompts import load_prompt
from paperfig.utils.types import CritiqueReport, FigurePlan, PaperContent


class CriticAgent:
    def __init__(self, threshold: float = 0.75, dimension_threshold: float = 0.55) -> None:
        self.threshold = threshold
        self.dimension_threshold = dimension_threshold
        self.prompt = load_prompt("critique_figure.txt")

    def critique(self, svg_path: Path, plan: FigurePlan, paper: PaperContent) -> CritiqueReport:
        svg_text = svg_path.read_text(encoding="utf-8")
        issues: List[str] = []
        recommendations: List[str] = []
        dimensions = self._score_dimensions(svg_text, plan, paper)
        score = sum(dimensions.values()) / len(dimensions)
        failed_dimensions = [name for name, value in dimensions.items() if value < self.dimension_threshold]

        if "readability" in failed_dimensions:
            issues.append("Readability below threshold: labels or visual structure are insufficient.")
            recommendations.append("Add clear labels, improve hierarchy, and avoid dense overlaps.")
        if "faithfulness" in failed_dimensions:
            issues.append("Faithfulness below threshold: figure support from source spans is weak.")
            recommendations.append("Tie every key label and relation to explicit source text spans.")
        if "conciseness" in failed_dimensions:
            issues.append("Conciseness below threshold: figure is either too sparse or overloaded.")
            recommendations.append("Keep only essential elements and remove decorative clutter.")
        if "aesthetics" in failed_dimensions:
            issues.append("Aesthetics below threshold: layout balance and presentation need refinement.")
            recommendations.append("Improve alignment, spacing, and consistent visual encoding.")

        passed = (
            score >= self.threshold
            and not failed_dimensions
            and not any("invalid" in issue.lower() for issue in issues)
        )

        if not passed:
            recommendations.append("Revise layout to improve clarity and alignment with the paper.")

        return CritiqueReport(
            figure_id=plan.figure_id,
            score=round(min(score, 1.0), 3),
            threshold=self.threshold,
            quality_dimensions={k: round(v, 3) for k, v in dimensions.items()},
            dimension_threshold=self.dimension_threshold,
            failed_dimensions=failed_dimensions,
            issues=issues,
            recommendations=recommendations,
            passed=passed,
        )

    def _score_dimensions(
        self,
        svg_text: str,
        plan: FigurePlan,
        paper: PaperContent,
    ) -> Dict[str, float]:
        return {
            "faithfulness": self._score_faithfulness(svg_text, plan, paper),
            "readability": self._score_readability(svg_text),
            "conciseness": self._score_conciseness(svg_text),
            "aesthetics": self._score_aesthetics(svg_text),
        }

    def _score_faithfulness(self, svg_text: str, plan: FigurePlan, paper: PaperContent) -> float:
        score = 0.35
        if plan.source_spans:
            score += 0.3
        if len(plan.description.strip()) > 20:
            score += 0.1
        if plan.kind == "results_plot" and paper.sections.get("results") and paper.sections["results"].text:
            score += 0.15
        if "mock paperbanana output" in svg_text.lower():
            score += 0.05
        return min(score, 1.0)

    def _score_readability(self, svg_text: str) -> float:
        score = 0.3
        text_count = svg_text.count("<text")
        if text_count >= 2:
            score += 0.25
        elif text_count == 1:
            score += 0.15
        if any(tag in svg_text for tag in ("<rect", "<path", "<line", "<circle")):
            score += 0.2
        if "font-size" in svg_text:
            score += 0.1
        if "viewBox" in svg_text:
            score += 0.1
        return min(score, 1.0)

    def _score_conciseness(self, svg_text: str) -> float:
        score = 0.5
        length = len(svg_text)
        if 250 <= length <= 9000:
            score += 0.25
        elif length > 12000:
            score -= 0.2
        else:
            score -= 0.1
        primitive_count = sum(svg_text.count(tag) for tag in ("<rect", "<path", "<line", "<circle", "<polygon"))
        if 1 <= primitive_count <= 40:
            score += 0.2
        elif primitive_count > 120:
            score -= 0.2
        return max(min(score, 1.0), 0.0)

    def _score_aesthetics(self, svg_text: str) -> float:
        score = 0.35
        if "viewBox" in svg_text and "width" in svg_text and "height" in svg_text:
            score += 0.2
        if "stroke" in svg_text:
            score += 0.15
        if "fill" in svg_text:
            score += 0.15
        if "font-family" in svg_text:
            score += 0.1
        return min(score, 1.0)
