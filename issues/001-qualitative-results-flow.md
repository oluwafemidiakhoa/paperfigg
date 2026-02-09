Title: Add a new qualitative results flow template with docs and tests
Labels: good first issue

Body:
Goal
Add a new flow template for qualitative results grids (e.g., side-by-side samples).

Scope
- Add `paperfig/templates/flows/qualitative_results_grid.yaml` using the schema.
- Add docs at `docs/architecture/flows/qualitative-results-grid/README.md` and `diagram.mermaid`.
- Add a test in `tests/test_templates.py` to assert selection when the results section contains "qualitative" or "samples".

Acceptance Criteria
- `paperfig templates lint` passes.
- `paperfig docs check` passes.
- New template is included in the flow template catalog in README auto-block.
- Unit test for template selection passes.

