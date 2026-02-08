from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from paperfig.agents.critic import CriticAgent
from paperfig.utils.types import FigurePlan, PaperContent, PaperSection


class CriticTests(unittest.TestCase):
    def _paper(self) -> PaperContent:
        return PaperContent(
            source_path="paper.md",
            full_text="full",
            sections={
                "methodology": PaperSection("methodology", "method text", 0, 11),
                "system": PaperSection("system", "system text", 12, 22),
                "results": PaperSection("results", "result text", 23, 34),
            },
        )

    def test_critique_returns_dimension_scores(self) -> None:
        plan = FigurePlan(
            figure_id="fig-1",
            title="System",
            kind="system_overview",
            order=1,
            abstraction_level="high",
            description="System layout",
            justification="Needed for architecture",
            source_spans=[{"section": "system", "start": 12, "end": 22, "quote": "system text"}],
        )

        svg = (
            "<svg viewBox='0 0 200 100' width='200' height='100'>"
            "<rect x='1' y='1' width='198' height='98' fill='white' stroke='black'/>"
            "<text x='10' y='20' font-size='12' font-family='Times'>A</text>"
            "<line x1='10' y1='30' x2='190' y2='30' stroke='black'/>"
            "</svg>"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "figure.svg"
            path.write_text(svg, encoding="utf-8")
            report = CriticAgent(threshold=0.6, dimension_threshold=0.5).critique(path, plan, self._paper())

        self.assertIn("faithfulness", report.quality_dimensions)
        self.assertIn("readability", report.quality_dimensions)
        self.assertIn("conciseness", report.quality_dimensions)
        self.assertIn("aesthetics", report.quality_dimensions)
        self.assertEqual(report.dimension_threshold, 0.5)
        self.assertTrue(report.passed)

    def test_dimension_gate_can_fail_even_with_low_threshold(self) -> None:
        plan = FigurePlan(
            figure_id="fig-2",
            title="Weak",
            kind="summary",
            order=1,
            abstraction_level="low",
            description="short",
            justification="test",
            source_spans=[],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "figure.svg"
            path.write_text("<svg></svg>", encoding="utf-8")
            report = CriticAgent(threshold=0.1, dimension_threshold=0.8).critique(path, plan, self._paper())

        self.assertFalse(report.passed)
        self.assertGreaterEqual(len(report.failed_dimensions), 1)


if __name__ == "__main__":
    unittest.main()
