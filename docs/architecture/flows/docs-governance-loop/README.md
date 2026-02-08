# Flow: Docs Governance Loop

## Purpose
Keep architecture and product docs synchronized with implementation through deterministic regeneration and drift detection.

## Inputs
- `docs/docs_manifest.yaml`
- Auto-gen block definitions
- Current markdown docs

## Outputs
- Updated docs (for regenerate mode)
- `docs_drift_report.json`
- Non-zero exit signal in check mode when drift is detected

## Agents Involved
- None (deterministic code path)

## Steps
1. Load manifest and document rules.
2. Render hybrid/generated blocks.
3. Validate required sections for every tracked doc.
4. Detect and report drift.
5. Optionally write regenerated content.

## AI vs Code Decisions
- AI decisions
  - None.

- Code decisions
  - Block rendering, validation, drift reporting, and gating policy.
