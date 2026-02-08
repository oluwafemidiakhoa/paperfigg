# AI Architecture Analysis: paperfig

## Purpose and Scope
`paperfig` is a production-grade CLI tool that converts a research paper (PDF or Markdown) into publication-ready academic figures using an agentic pipeline. The system produces a figure pack that includes SVG and PNG assets, LaTeX include snippets, captions, and full traceability back to source text spans.

This document describes the system at a high level, the agents and their responsibilities, the data flow, and the rationale for using agentic decomposition. It also documents assumptions and failure modes that must be considered in production deployments.

## System Overview
The system has seven primary stages, each represented as a documented flow in `docs/architecture/flows`:

1. Paper ingestion and section extraction.
2. Autonomous figure planning.
3. Figure generation with critique-driven iteration.
4. Export and traceability packaging.
5. Documentation governance and drift gating.
6. Architecture critique and reproducibility auditing.
7. Autonomous lab experimentation scaffold.

The core of the system is an agentic loop that plans, generates, and critiques figures until a quality threshold is met.

## Agents and Responsibilities
The system uses three core agents, each implemented as a class:

- `PlannerAgent` (`paperfig/agents/planner.py`)
  - Inputs: extracted paper sections and metadata
  - Outputs: a structured figure plan, including figure types, ordering, and justifications
  - Responsibility: decide which figures to create, define their purpose, and tie each decision to source text spans

- `GeneratorAgent` (`paperfig/agents/generator.py`)
  - Inputs: figure plan, source sections, and style references
  - Outputs: candidate figures in SVG format plus structured traceability metadata
  - Responsibility: generate figure drafts via PaperBanana (invoked through the MCP server)

- `CriticAgent` (`paperfig/agents/critic.py`)
  - Inputs: candidate figure, source sections, and traceability
  - Outputs: critique report with scores and actionable issues
  - Responsibility: evaluate faithfulness, readability, conciseness, and aesthetics; decide whether another generation iteration is required

- `ArchitectureCriticAgent` (`paperfig/agents/architecture_critic.py`)
  - Inputs: run-level artifacts, inspect summary, and governance metadata
  - Outputs: severity-tagged architecture findings with evidence and suggestions
  - Responsibility: enforce architecture governance quality thresholds

## Data Flow and Interfaces
1. Ingestion
   - PDF or Markdown is parsed into raw text.
   - A section extractor identifies and stores methodology, system description, and results sections.
   - Each section is stored with explicit character spans for traceability.

2. Planning
   - The `PlannerAgent` produces a `FigurePlan` list.
   - Each plan entry includes a justification, figure type, a sketch-level structure, and the text spans that motivated it.

3. Generation
   - For each plan entry, `GeneratorAgent` builds a structured request and calls PaperBanana via MCP.
   - Style references are loaded from versioned presets in `paperfig/styles` or a configured override file.
   - MCP transport is runtime-configurable via environment-based client factory or stdio SDK client settings.
   - The generation response is expected to include an SVG plus structured figure element metadata.

4. Critique and Iteration
   - The `CriticAgent` scores the candidate and produces a critique report.
   - The report includes per-dimension scores for faithfulness, readability, conciseness, and aesthetics.
   - If the report fails the quality threshold or contains blocking issues, the figure is regenerated with revised guidance.
   - Acceptance requires both an overall threshold pass and per-dimension threshold pass.
   - Critique issues and recommendations are injected into the next generation request, creating a closed-loop revision cycle.

5. Export
   - SVG and PNG are exported.
   - LaTeX include snippets and captions are written.
   - Traceability JSON is compiled, mapping each figure element to source spans.
   - A run-level `inspect.json` summary is persisted for audit and debugging.

6. Documentation Governance
   - Docs manifest rules are applied to all tracked docs.
   - Hybrid auto-generated blocks are rendered and validated.
   - Drift reports are persisted as `docs_drift_report.json`.

7. Architecture Critique + Reproducibility
   - Architecture critique emits severity-tagged governance findings.
   - Reproducibility audit checks environment capture, artifact completeness, and provenance metadata.
   - Enforcement is mode-based (`soft`/`hard`) and threshold-based (`critical` default for architecture blocking).

8. Autonomous Lab Scaffold
   - Lab runs are initialized with policy-constrained execution.
   - Agents propose, run, and review experiments with persistent logs and registry updates.

## Why Agentic Decomposition
The system uses agentic decomposition for three reasons:

1. Separation of concerns
   - Planning requires semantic interpretation of the paper, while generation requires graphical synthesis. Keeping these separate allows specialized prompts and scoring.

2. Iterative improvement
   - Figures often require multiple attempts. A dedicated critique agent enables structured, auditable iteration rather than ad-hoc retries.

3. Traceability
   - The planner and critic create explicit links between source text and figure elements, enabling robust audit trails.

Agentic decomposition provides modularity, auditability, and improved quality control. It also allows future replacement of individual agents without redesigning the entire pipeline.
The lab scaffold extends this approach to autonomous experimentation while preserving strict execution policy controls.

## Assumptions
- Papers follow conventional academic structure with recognizable headings.
- PaperBanana MCP server provides stable SVG output and element metadata.
- Style references are either preconfigured or retrievable in a controlled environment.
- The runtime environment has access to any required PDF parsing and SVG rendering libraries.

## Failure Modes and Mitigations
- Section extraction fails due to unconventional headings
  - Mitigation: fallback heuristics and manual override options in future releases.

- Planner produces irrelevant or missing figures
  - Mitigation: constrain planning prompts and log plan decisions for manual review.

- Generator produces low-quality or off-topic figures
  - Mitigation: critique loop with strict thresholds and structured error feedback.

- PaperBanana service unavailable
  - Mitigation: fail fast with clear errors; allow queued retries in a production scheduler.

- Traceability mismatch between figure elements and source spans
  - Mitigation: enforce traceability schema validation and reject incomplete figure drafts.

- Export conversion errors (SVG to PNG)
  - Mitigation: optional dependency checks and explicit failure messages.

## Versioning and Auditability
All agent decisions, prompts, flow diagrams, and traceability artifacts are plain files in the repository or run outputs. This ensures the architecture and reasoning are fully versioned, inspectable, and reproducible.
