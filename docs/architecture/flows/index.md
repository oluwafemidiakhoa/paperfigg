# System Flows

This index lists the core flows that make up the `paperfig` system. Each flow is documented with a step-by-step README and a Mermaid diagram.

- [paper-to-figure-pack/](paper-to-figure-pack/README.md)
  - Ingestion, section extraction, planning, and initial figure pack creation.

- [figure-generation-loop/](figure-generation-loop/README.md)
  - Agentic loop for figure drafting with PaperBanana and structured element metadata.

- [figure-critique-loop/](figure-critique-loop/README.md)
  - Critique, scoring, and iterative revision process.

- [export-and-traceability/](export-and-traceability/README.md)
  - Export of SVG/PNG/LaTeX and assembly of traceability JSON.

- [docs-governance-loop/](docs-governance-loop/README.md)
  - Auto-regeneration and drift-gating flow for architecture and product docs.

- [architecture-critique-and-repro-audit/](architecture-critique-and-repro-audit/README.md)
  - Run-level architecture governance and reproducibility audit checks.

- [autonomous-lab-loop/](autonomous-lab-loop/README.md)
  - Constrained autonomous experiment lifecycle with policy enforcement.
