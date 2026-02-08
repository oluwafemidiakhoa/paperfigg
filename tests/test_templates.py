from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from paperfig.templates.compiler import select_templates
from paperfig.templates.loader import load_template_catalog, validate_template_catalog
from paperfig.utils.types import PaperContent, PaperSection


class TemplateTests(unittest.TestCase):
    def test_load_expanded_template_catalog(self) -> None:
        catalog = load_template_catalog(Path("paperfig/templates/flows"), pack_id="expanded_v1")
        self.assertEqual(catalog.pack_id, "expanded_v1")
        self.assertEqual(len(catalog.templates), 8)

    def test_validate_template_catalog(self) -> None:
        errors = validate_template_catalog(Path("paperfig/templates/flows"), pack_id="expanded_v1")
        self.assertEqual(errors, [])

    def test_template_selection_for_common_sections(self) -> None:
        paper = PaperContent(
            source_path="paper.md",
            full_text="",
            sections={
                "methodology": PaperSection(
                    name="methodology",
                    text="Our pipeline trains on dataset and reports compute.",
                    start=0,
                    end=60,
                ),
                "system": PaperSection(
                    name="system",
                    text="The system architecture has modules and data flow.",
                    start=61,
                    end=120,
                ),
                "results": PaperSection(
                    name="results",
                    text="Results show improved benchmark score and ablation details.",
                    start=121,
                    end=200,
                ),
            },
        )

        catalog = load_template_catalog(Path("paperfig/templates/flows"), pack_id="expanded_v1")
        selected = select_templates(catalog.templates, paper)
        selected_ids = {item.template_id for item in selected}

        self.assertIn("methodology_pipeline", selected_ids)
        self.assertIn("system_overview", selected_ids)
        self.assertIn("results_summary_plot", selected_ids)


if __name__ == "__main__":
    unittest.main()
