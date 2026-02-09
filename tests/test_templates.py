from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

from paperfig.templates.compiler import select_templates
from paperfig.templates.lint import lint_template_catalog
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

    def test_templates_lint_passes_for_builtin_catalog(self) -> None:
        errors = lint_template_catalog(Path("paperfig/templates/flows"))
        self.assertEqual(errors, [])

    def test_templates_lint_reports_file_and_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            template_dir = Path(tmpdir)
            bad_path = template_dir / "bad.yaml"
            bad_path.write_text('{"id":"bad","name":"Bad","type":"x","inputs":{}}', encoding="utf-8")

            errors = lint_template_catalog(template_dir)
            self.assertGreaterEqual(len(errors), 1)
            self.assertTrue(any("bad.yaml" in error for error in errors))
            self.assertTrue(any("steps" in error or "outputs" in error or "metadata" in error for error in errors))

    def test_templates_list_supports_pack_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pack_root = Path(tmpdir) / "ai-pack"
            flows_dir = pack_root / "templates" / "flows"
            flows_dir.mkdir(parents=True, exist_ok=True)
            (flows_dir / "ai.yaml").write_text(
                (
                    "{"
                    '"id":"ai_flow",'
                    '"name":"AI Flow",'
                    '"type":"system_overview",'
                    '"inputs":{"required_sections":["system"]},'
                    '"steps":[{"id":"trigger","kind":"trigger","rules":[]}],'
                    '"outputs":{"figure_kind":"system_overview","caption_style":"concise"},'
                    '"scoring":{"critique_focus":["faithfulness"]},'
                    '"metadata":{"pack":"ai_pack","order_hint":1,"trigger_rules":[],"caption_style":"concise","traceability_requirements":{},"critique_focus":["faithfulness"],"required_sections":["system"],"element_blueprint":{"nodes":[]}}'
                    "}"
                ),
                encoding="utf-8",
            )

            catalog = load_template_catalog(
                template_dir=Path("paperfig/templates/flows"),
                pack_id="expanded_v1",
                pack=str(pack_root),
            )
            self.assertEqual(len(catalog.templates), 1)
            self.assertEqual(catalog.templates[0].template_id, "ai_flow")

    def test_templates_list_supports_pack_python_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pkg = root / "mock_pack"
            flows_dir = pkg / "templates" / "flows"
            flows_dir.mkdir(parents=True, exist_ok=True)
            (pkg / "__init__.py").write_text("", encoding="utf-8")
            (flows_dir / "pkg.yaml").write_text(
                (
                    "{"
                    '"id":"pkg_flow",'
                    '"name":"Package Flow",'
                    '"type":"results_plot",'
                    '"inputs":{"required_sections":["results"]},'
                    '"steps":[{"id":"trigger","kind":"trigger","rules":[]}],'
                    '"outputs":{"figure_kind":"results_plot","caption_style":"brief"},'
                    '"scoring":{"critique_focus":["conciseness"]},'
                    '"metadata":{"pack":"pkg_pack","order_hint":1,"trigger_rules":[],"caption_style":"brief","traceability_requirements":{},"critique_focus":["conciseness"],"required_sections":["results"],"element_blueprint":{"nodes":[]}}'
                    "}"
                ),
                encoding="utf-8",
            )

            sys.path.insert(0, str(root))
            try:
                catalog = load_template_catalog(
                    template_dir=Path("paperfig/templates/flows"),
                    pack_id="expanded_v1",
                    pack="mock_pack",
                )
            finally:
                sys.path.remove(str(root))

            self.assertEqual(len(catalog.templates), 1)
            self.assertEqual(catalog.templates[0].template_id, "pkg_flow")


if __name__ == "__main__":
    unittest.main()
