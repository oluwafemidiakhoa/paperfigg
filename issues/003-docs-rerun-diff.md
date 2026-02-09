Title: Add rerun and diff usage docs and link from README
Labels: good first issue

Body:
Goal
Document deterministic replay and diff workflows for users and contributors.

Scope
- Add doc: `docs/reproducibility/RERUN_DIFF.md` describing:
  - `paperfig rerun <run_id>`
  - `paperfig diff <run_id_1> <run_id_2>`
  - Where `diff.json` is written
- Update `docs/docs_manifest.yaml` to include the new doc.
- Add a short "Rerun + Diff" section in `README.md` (outside auto-gen blocks).

Acceptance Criteria
- `paperfig docs check` passes.
- New doc is discoverable from README.

