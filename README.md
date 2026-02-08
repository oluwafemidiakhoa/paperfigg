# paperfig
[![CI Workflow](https://img.shields.io/badge/CI-workflow-blue?logo=githubactions)](.github/workflows/ci.yml)
[![Docs Drift Workflow](https://img.shields.io/badge/Docs%20Drift-workflow-blue?logo=githubactions)](.github/workflows/docs-drift.yml)

`paperfig` is a production-grade CLI that converts research papers (PDF or Markdown) into publication-ready academic figures using an agentic planning -> generation -> critique pipeline. It outputs SVG, transparent PNG, LaTeX include snippets, captions, and full traceability mappings from figure elements back to source text spans.

## What It Does
- Parses papers and extracts methodology, system description, and results sections.
- Plans figures through reusable flow templates and fallback heuristics.
- Generates figures via PaperBanana MCP and iterates with critique feedback loops.
- Regenerates docs and gates on drift for architecture governance.
- Runs reproducibility audits and architecture critiques as first-class run artifacts.
- Provides a constrained autonomous lab scaffold for iterative research experiments.

## How The Agentic System Works
The system uses specialized agents:
- `PlannerAgent` chooses figures and template-aligned abstractions.
- `GeneratorAgent` calls PaperBanana via MCP and emits traceable figure elements.
- `CriticAgent` scores faithfulness, readability, conciseness, and aesthetics.
- `ArchitectureCriticAgent` audits run-level architecture quality and governance completeness.

Full architecture documentation and flow diagrams live in `docs/architecture`.

## CLI Usage
<!-- AUTO-GEN:START cli-command-catalog -->
- `paperfig generate`
- `paperfig critique`
- `paperfig export`
- `paperfig inspect`
- `paperfig docs regenerate`
- `paperfig docs check`
- `paperfig templates list`
- `paperfig templates validate`
- `paperfig critique-architecture`
- `paperfig audit`
- `paperfig lab init`
- `paperfig lab propose`
- `paperfig lab run`
- `paperfig lab review`
- `paperfig lab status`
<!-- AUTO-GEN:END cli-command-catalog -->

## Flow Template Pack
<!-- AUTO-GEN:START flow-template-catalog -->
- `ablation_matrix` (ablation)
- `dataset_characteristics` (dataset_overview)
- `error_analysis_breakdown` (error_analysis)
- `limitations_threats_to_validity` (limitations)
- `methodology_pipeline` (methodology)
- `results_summary_plot` (results_plot)
- `system_overview` (system_overview)
- `training_compute_profile` (compute_profile)
<!-- AUTO-GEN:END flow-template-catalog -->

## Outputs
Each run creates a `runs/<run_id>/` workspace containing:
- `figures/<figure_id>/figure.svg`
- `figures/<figure_id>/traceability.json`
- `captions.txt`
- `inspect.json`
- `docs_drift_report.json`
- `architecture_critique.json`
- `repro_audit.json`
- `exports/` with PNG, SVG, LaTeX snippets, and `export_report.json`

## Configuration
Default config lives in `paperfig.yaml`:
- docs scope and manifest path (`docs/docs_manifest.yaml`)
- architecture critique mode and severity gate
- reproducibility audit mode (`soft` by default)
- template pack (`expanded_v1`)
- lab registry path and sandbox policy (`config/lab_policy.yaml`)

## Verification
- Run unit/integration tests: `python3 -m unittest discover -s tests -v`
- Run docs drift check: `./scripts/check_docs_drift.sh`
- Run full quality checks: `./scripts/check_quality.sh`

## CI
- GitHub Actions pipeline: `.github/workflows/ci.yml`
- GitLab pipeline: `.gitlab-ci.yml`
- Both use the same quality gate script: `./scripts/check_quality.sh`

## Architecture Docs
See:
- `docs/architecture/AI-Architecture-Analysis.md`
- `docs/architecture/flows/index.md`
