from __future__ import annotations

import json
import shutil
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from paperfig.agents.architecture_critic import ArchitectureCriticAgent, report_to_dict as architecture_report_to_dict
from paperfig.agents.critic import CriticAgent
from paperfig.agents.generator import GeneratorAgent
from paperfig.agents.planner import PlannerAgent
from paperfig.audits.reproducibility import report_to_dict as repro_report_to_dict
from paperfig.audits.reproducibility import run_reproducibility_audit
from paperfig.docsgen import run_docs_regeneration
from paperfig.exporters.latex import export_latex
from paperfig.exporters.png import export_png
from paperfig.exporters.svg import export_svg
from paperfig.utils.config import config_hash, load_config
from paperfig.utils.pdf_parser import parse_paper
from paperfig.utils.style_refs import load_style_refs
from paperfig.utils.types import CritiqueReport, FigurePlan


class Orchestrator:
    def __init__(
        self,
        run_root: Path = Path("runs"),
        max_iterations: int = 3,
        quality_threshold: float = 0.75,
        dimension_threshold: float = 0.55,
        template_pack: Optional[str] = None,
        arch_critique_mode: Optional[str] = None,
        arch_critique_block_severity: Optional[str] = None,
        repro_audit_mode: Optional[str] = None,
        config_path: Path = Path("paperfig.yaml"),
    ) -> None:
        self.run_root = run_root
        self.max_iterations = max_iterations
        self.quality_threshold = quality_threshold
        self.dimension_threshold = dimension_threshold
        self.config_path = config_path

        self.config = load_config(config_path)
        self.config_fingerprint = config_hash(self.config)

        template_cfg = self.config.get("templates", {})
        self.template_pack = template_pack or str(template_cfg.get("active_pack", "expanded_v1"))
        self.template_dir = Path(str(template_cfg.get("template_dir", "paperfig/templates/flows")))

        arch_cfg = self.config.get("architecture_critique", {})
        self.arch_critique_mode = arch_critique_mode or (
            "inline" if bool(arch_cfg.get("inline_on_generate", True)) else "off"
        )
        self.arch_critique_block_severity = arch_critique_block_severity or str(
            arch_cfg.get("block_severity", "critical")
        )
        self.arch_critique_output_file = str(arch_cfg.get("output_file", "architecture_critique.json"))

        repro_cfg = self.config.get("reproducibility", {})
        self.repro_audit_mode = repro_audit_mode or str(repro_cfg.get("mode", "soft"))
        self.repro_audit_output_file = str(repro_cfg.get("output_file", "repro_audit.json"))

        docs_cfg = self.config.get("docs", {})
        self.docs_manifest_path = Path(str(docs_cfg.get("manifest_path", "docs/docs_manifest.yaml")))
        self.docs_auto_regen_on_generate = bool(docs_cfg.get("auto_regen_on_generate", True))

        self.planner = PlannerAgent(template_dir=self.template_dir, template_pack=self.template_pack)
        self.generator = GeneratorAgent()
        self.critic = CriticAgent(
            threshold=quality_threshold,
            dimension_threshold=dimension_threshold,
        )
        self.architecture_critic = ArchitectureCriticAgent()

    def generate(self, paper_path: Path) -> str:
        paper = parse_paper(paper_path)
        plan = self.planner.plan(paper)
        style_refs = load_style_refs()
        run_id = self._new_run_id()
        run_dir = self.run_root / run_id
        figures_dir = run_dir / "figures"
        exports_dir = run_dir / "exports"

        figures_dir.mkdir(parents=True, exist_ok=True)
        exports_dir.mkdir(parents=True, exist_ok=True)

        self._write_run_metadata(run_dir, paper_path)
        self._write_sections(run_dir, paper)
        self._write_plan(run_dir, plan)
        self._write_prompts(run_dir)
        self._write_style_refs(run_dir, style_refs)

        captions: List[str] = []
        traceability_records: List[dict] = []

        for figure_plan in plan:
            figure_dir = figures_dir / figure_plan.figure_id
            figure_dir.mkdir(parents=True, exist_ok=True)
            accepted = False
            last_report: CritiqueReport | None = None
            critique_feedback: dict | None = None

            for iteration in range(1, self.max_iterations + 1):
                iter_dir = figure_dir / f"iter_{iteration}"
                candidate = self.generator.generate(
                    figure_plan,
                    paper,
                    iter_dir,
                    iteration,
                    style_refs=style_refs,
                    critique_feedback=critique_feedback,
                )
                report = self.critic.critique(Path(candidate.svg_path), figure_plan, paper)
                last_report = report
                critique_feedback = {
                    "previous_score": report.score,
                    "issues": report.issues,
                    "recommendations": report.recommendations,
                    "failed_dimensions": report.failed_dimensions,
                }

                critique_path = iter_dir / "critique.json"
                with open(critique_path, "w", encoding="utf-8") as handle:
                    json.dump(asdict(report), handle, indent=2)

                if report.passed:
                    final_dir = figure_dir / "final"
                    final_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(candidate.svg_path, final_dir / "figure.svg")
                    shutil.copy2(candidate.element_metadata_path, final_dir / "element_metadata.json")
                    shutil.copy2(candidate.traceability_path, final_dir / "traceability.json")
                    accepted = True
                    break

            if not accepted and last_report:
                final_dir = figure_dir / "final"
                final_dir.mkdir(parents=True, exist_ok=True)
                # Fall back to the last iteration artifacts for traceability.
                last_iter_dir = figure_dir / f"iter_{self.max_iterations}"
                shutil.copy2(last_iter_dir / "figure.svg", final_dir / "figure.svg")
                shutil.copy2(last_iter_dir / "element_metadata.json", final_dir / "element_metadata.json")
                shutil.copy2(last_iter_dir / "traceability.json", final_dir / "traceability.json")

            captions.append(f"{figure_plan.figure_id}: {figure_plan.title} - {figure_plan.justification}")

            traceability_path = figure_dir / "final" / "traceability.json"
            if traceability_path.exists():
                with open(traceability_path, "r", encoding="utf-8") as handle:
                    traceability_records.append(json.load(handle))

        captions_path = run_dir / "captions.txt"
        captions_path.write_text("\n".join(captions), encoding="utf-8")

        traceability_path = run_dir / "traceability.json"
        with open(traceability_path, "w", encoding="utf-8") as handle:
            json.dump({"figures": traceability_records}, handle, indent=2)

        # Finalization order: inspect -> docs check/regeneration -> architecture critique -> reproducibility audit.
        self._write_inspect_snapshot(run_id=run_id)

        docs_report = self.docs_regenerate(check_only=not self.docs_auto_regen_on_generate)
        self._write_json(run_dir / "docs_drift_report.json", docs_report)
        if docs_report.get("drift_detected"):
            raise RuntimeError(
                "Documentation drift detected and docs were regenerated. "
                "Review and commit documentation updates before rerunning."
            )

        if self.arch_critique_mode == "inline":
            architecture_report = self.critique_architecture(
                run_id,
                block_severity=self.arch_critique_block_severity,
                persist=True,
            )
            if architecture_report.get("blocked"):
                raise RuntimeError(
                    "Architecture critique blocked this run at severity threshold "
                    f"'{self.arch_critique_block_severity}'."
                )

        repro_report = self.audit(run_id, mode=self.repro_audit_mode, persist=True)
        if self.repro_audit_mode == "hard" and not repro_report.get("passed", False):
            raise RuntimeError("Reproducibility audit failed in hard mode.")

        return run_id

    def docs_regenerate(
        self,
        check_only: bool = False,
        report_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        report = run_docs_regeneration(
            manifest_path=self.docs_manifest_path,
            check_only=check_only,
            repo_root=Path("."),
        )

        if report_path:
            self._write_json(report_path, report)
        return report

    def critique_architecture(
        self,
        run_id: str,
        block_severity: Optional[str] = None,
        persist: bool = True,
    ) -> Dict[str, Any]:
        run_dir = self.run_root / run_id
        if not run_dir.exists():
            raise FileNotFoundError(f"Run {run_id} not found in {self.run_root}")

        threshold = block_severity or self.arch_critique_block_severity
        report_obj = self.architecture_critic.critique(run_dir=run_dir, block_severity=threshold)
        report = architecture_report_to_dict(report_obj)

        if persist:
            self._write_json(run_dir / self.arch_critique_output_file, report)
        return report

    def audit(
        self,
        run_id: str,
        mode: Optional[str] = None,
        persist: bool = True,
    ) -> Dict[str, Any]:
        run_dir = self.run_root / run_id
        if not run_dir.exists():
            raise FileNotFoundError(f"Run {run_id} not found in {self.run_root}")

        selected_mode = mode or self.repro_audit_mode
        report_obj = run_reproducibility_audit(
            run_dir=run_dir,
            mode=selected_mode,
            expected_config_hash=self.config_fingerprint,
        )
        report = repro_report_to_dict(report_obj)

        if persist:
            self._write_json(run_dir / self.repro_audit_output_file, report)
        return report

    def export(self, run_id: str, output_dir: Path | None = None) -> Path:
        run_dir = self.run_root / run_id
        if not run_dir.exists():
            raise FileNotFoundError(f"Run {run_id} not found in {self.run_root}")

        output_dir = output_dir or (run_dir / "exports")
        output_dir.mkdir(parents=True, exist_ok=True)
        export_report = {
            "run_id": run_id,
            "output_dir": str(output_dir),
            "figures": [],
            "warnings": [],
        }

        plan_path = run_dir / "plan.json"
        if plan_path.exists():
            plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
            plan_by_id = {item["figure_id"]: item for item in plan_data}
        else:
            plan_by_id = {}

        figures_dir = run_dir / "figures"
        if figures_dir.exists():
            for figure_dir in figures_dir.iterdir():
                final_dir = figure_dir / "final"
                svg_path = final_dir / "figure.svg"
                if not svg_path.exists():
                    continue

                figure_id = figure_dir.name
                target_svg = output_dir / f"{figure_id}.svg"
                export_svg(svg_path, target_svg)
                figure_report = {
                    "figure_id": figure_id,
                    "svg": str(target_svg),
                    "png": None,
                    "latex": str(output_dir / f"{figure_id}.tex"),
                }

                try:
                    png_path = output_dir / f"{figure_id}.png"
                    export_png(svg_path, png_path)
                    figure_report["png"] = str(png_path)
                except RuntimeError as exc:
                    export_report["warnings"].append(
                        f"PNG export skipped for {figure_id}: {exc}"
                    )

                plan_entry = plan_by_id.get(figure_id, {})
                caption = plan_entry.get("title", figure_id)
                export_latex(figure_id, f"{figure_id}.svg", caption, output_dir / f"{figure_id}.tex")

                traceability_src = final_dir / "traceability.json"
                if traceability_src.exists():
                    shutil.copy2(traceability_src, output_dir / f"{figure_id}.traceability.json")
                export_report["figures"].append(figure_report)

        captions_src = run_dir / "captions.txt"
        if captions_src.exists():
            shutil.copy2(captions_src, output_dir / "captions.txt")

        traceability_src = run_dir / "traceability.json"
        if traceability_src.exists():
            shutil.copy2(traceability_src, output_dir / "traceability.json")

        with open(output_dir / "export_report.json", "w", encoding="utf-8") as handle:
            json.dump(export_report, handle, indent=2)

        return output_dir

    def inspect(
        self,
        run_id: str,
        failures_only: bool = False,
        figure_id: Optional[str] = None,
        min_score: Optional[float] = None,
        failed_dimension: Optional[str] = None,
    ) -> dict:
        run_dir = self.run_root / run_id
        if not run_dir.exists():
            raise FileNotFoundError(f"Run {run_id} not found in {self.run_root}")

        summary = {
            "run_id": run_id,
            "run_dir": str(run_dir),
            "metadata": {},
            "plan_count": 0,
            "figures": [],
            "aggregate": {},
            "warnings": [],
        }

        run_meta_path = run_dir / "run.json"
        if run_meta_path.exists():
            summary["metadata"] = json.loads(run_meta_path.read_text(encoding="utf-8"))
        else:
            summary["warnings"].append("Missing run metadata: run.json")
        run_max_iterations = int(summary["metadata"].get("max_iterations", self.max_iterations))

        plan_path = run_dir / "plan.json"
        plan_by_id: dict = {}
        if plan_path.exists():
            plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
            summary["plan_count"] = len(plan_data)
            plan_by_id = {item["figure_id"]: item for item in plan_data}
        else:
            summary["warnings"].append("Missing plan: plan.json")

        figures_dir = run_dir / "figures"
        if not figures_dir.exists():
            summary["warnings"].append("Missing figures directory.")
            return summary

        figure_summaries = []
        figure_id_filter = figure_id
        for figure_dir in sorted(figures_dir.iterdir()):
            if not figure_dir.is_dir():
                continue
            current_figure_id = figure_dir.name
            plan_entry = plan_by_id.get(current_figure_id, {})

            iter_reports = []
            iter_dirs = sorted(
                [p for p in figure_dir.glob("iter_*") if p.is_dir()],
                key=lambda p: int(p.name.split("_")[1]) if "_" in p.name and p.name.split("_")[1].isdigit() else 0,
            )
            for iter_dir in iter_dirs:
                critique_path = iter_dir / "critique.json"
                if not critique_path.exists():
                    summary["warnings"].append(f"Missing critique file: {critique_path}")
                    continue
                report = json.loads(critique_path.read_text(encoding="utf-8"))
                report["iteration"] = int(iter_dir.name.split("_")[1]) if "_" in iter_dir.name else 0
                iter_reports.append(report)

            last_report = iter_reports[-1] if iter_reports else {}
            accepted = bool(last_report.get("passed", False))

            final_dir = figure_dir / "final"
            final_svg = final_dir / "figure.svg"
            element_metadata_path = final_dir / "element_metadata.json"
            traceability_path = final_dir / "traceability.json"

            total_elements = 0
            traced_elements = 0

            if element_metadata_path.exists():
                element_metadata = json.loads(element_metadata_path.read_text(encoding="utf-8"))
                if isinstance(element_metadata, list):
                    total_elements = len(element_metadata)

            if traceability_path.exists():
                traceability = json.loads(traceability_path.read_text(encoding="utf-8"))
                trace_elements = traceability.get("elements", [])
                if isinstance(trace_elements, list):
                    if total_elements == 0:
                        total_elements = len(trace_elements)
                    traced_elements = sum(
                        1 for element in trace_elements if isinstance(element.get("source_spans"), list) and element["source_spans"]
                    )

            coverage = (traced_elements / total_elements) if total_elements else None
            max_iterations_hit = bool(iter_reports) and len(iter_reports) >= run_max_iterations and not accepted

            figure_summary = {
                "figure_id": current_figure_id,
                "title": plan_entry.get("title", current_figure_id),
                "kind": plan_entry.get("kind", "unknown"),
                "template_id": plan_entry.get("template_id", ""),
                "iterations_attempted": len(iter_reports),
                "max_iterations_hit": max_iterations_hit,
                "accepted": accepted,
                "final_score": last_report.get("score"),
                "final_passed": last_report.get("passed"),
                "failed_dimensions": last_report.get("failed_dimensions", []),
                "issues": last_report.get("issues", []),
                "recommendations": last_report.get("recommendations", []),
                "traceability": {
                    "total_elements": total_elements,
                    "traced_elements": traced_elements,
                    "coverage": coverage,
                },
                "iteration_history": [
                    {
                        "iteration": report.get("iteration"),
                        "score": report.get("score"),
                        "passed": report.get("passed"),
                        "failed_dimensions": report.get("failed_dimensions", []),
                    }
                    for report in iter_reports
                ],
                "final_svg_path": str(final_svg) if final_svg.exists() else None,
            }
            figure_summaries.append(figure_summary)

        if figure_id_filter:
            figure_summaries = [item for item in figure_summaries if item.get("figure_id") == figure_id_filter]
        if failures_only:
            figure_summaries = [item for item in figure_summaries if not item.get("final_passed")]
        if min_score is not None:
            figure_summaries = [
                item
                for item in figure_summaries
                if isinstance(item.get("final_score"), (int, float)) and item["final_score"] >= min_score
            ]
        if failed_dimension:
            target = failed_dimension.strip().lower()
            figure_summaries = [
                item
                for item in figure_summaries
                if any(str(dim).lower() == target for dim in (item.get("failed_dimensions") or []))
            ]

        summary["figures"] = figure_summaries
        accepted_count = sum(1 for item in figure_summaries if item.get("final_passed"))
        total_figures = len(figure_summaries)
        final_scores = [item["final_score"] for item in figure_summaries if isinstance(item.get("final_score"), (int, float))]
        coverage_values = [
            item["traceability"]["coverage"]
            for item in figure_summaries
            if isinstance(item["traceability"].get("coverage"), (int, float))
        ]

        summary["aggregate"] = {
            "total_figures": total_figures,
            "accepted_count": accepted_count,
            "failed_count": total_figures - accepted_count,
            "avg_final_score": (sum(final_scores) / len(final_scores)) if final_scores else None,
            "avg_traceability_coverage": (sum(coverage_values) / len(coverage_values)) if coverage_values else None,
            "max_iterations_hit": [item["figure_id"] for item in figure_summaries if item.get("max_iterations_hit")],
        }

        return summary

    def _write_run_metadata(self, run_dir: Path, paper_path: Path) -> None:
        metadata = {
            "run_id": run_dir.name,
            "paper_path": str(paper_path),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "max_iterations": self.max_iterations,
            "quality_threshold": self.quality_threshold,
            "dimension_threshold": self.dimension_threshold,
            "template_pack": self.template_pack,
            "arch_critique_mode": self.arch_critique_mode,
            "arch_critique_block_severity": self.arch_critique_block_severity,
            "repro_audit_mode": self.repro_audit_mode,
            "config_hash": self.config_fingerprint,
            "seed": None,
        }
        self._write_json(run_dir / "run.json", metadata)

    def _write_sections(self, run_dir: Path, paper) -> None:
        sections = {name: asdict(section) for name, section in paper.sections.items()}
        self._write_json(run_dir / "sections.json", sections)

    def _write_plan(self, run_dir: Path, plan: List[FigurePlan]) -> None:
        self._write_json(run_dir / "plan.json", [asdict(item) for item in plan])

    def _write_prompts(self, run_dir: Path) -> None:
        prompt_dir = run_dir / "prompts"
        prompt_dir.mkdir(parents=True, exist_ok=True)
        from paperfig.utils.prompts import load_prompt

        (prompt_dir / "plan_figure.txt").write_text(load_prompt("plan_figure.txt"), encoding="utf-8")
        (prompt_dir / "critique_figure.txt").write_text(load_prompt("critique_figure.txt"), encoding="utf-8")
        try:
            (prompt_dir / "critique_architecture.txt").write_text(
                load_prompt("critique_architecture.txt"),
                encoding="utf-8",
            )
        except FileNotFoundError:
            pass
        try:
            (prompt_dir / "repro_audit.txt").write_text(
                load_prompt("repro_audit.txt"),
                encoding="utf-8",
            )
        except FileNotFoundError:
            pass

    def _new_run_id(self) -> str:
        return f"run-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"

    def _write_style_refs(self, run_dir: Path, style_refs: dict) -> None:
        self._write_json(run_dir / "style_refs.json", style_refs)

    def _write_inspect_snapshot(self, run_id: str) -> None:
        run_dir = self.run_root / run_id
        snapshot = self.inspect(run_id)
        self._write_json(run_dir / "inspect.json", snapshot)

    @staticmethod
    def _write_json(path: Path, data: Dict[str, Any] | List[Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
