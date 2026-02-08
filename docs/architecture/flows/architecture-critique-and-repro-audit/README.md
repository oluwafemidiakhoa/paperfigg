# Flow: Architecture Critique and Repro Audit

## Purpose
Provide governance-grade post-generation checks for architecture quality and reproducibility.

## Inputs
- Run artifacts (`plan.json`, `inspect.json`, prompts, traceability, docs drift report)
- Configuration thresholds and audit mode

## Outputs
- `architecture_critique.json`
- `repro_audit.json`
- Optional blocking failure based on configured gates

## Agents Involved
- ArchitectureCriticAgent

## Steps
1. Evaluate run-level architecture quality and artifact completeness.
2. Emit severity-tagged findings with evidence and suggestions.
3. Enforce severity gate (`critical` default).
4. Run reproducibility checks on provenance, completeness, and environment capture.
5. Enforce audit mode (`soft` warning or `hard` failure).

## AI vs Code Decisions
- AI decisions
  - Architecture critique findings and severity rationale.

- Code decisions
  - Severity threshold enforcement and reproducibility check execution.
