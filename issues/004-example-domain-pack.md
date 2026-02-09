Title: Add example domain pack under examples and validate pack discovery
Labels: good first issue

Body:
Goal
Provide a concrete, runnable example of a domain pack.

Scope
- Add an example pack at `examples/template_packs/ai/` with:
  - `templates/flows/ai_system_overview.yaml`
  - Optional README explaining usage
- Update `docs/templates/DOMAIN_PACKS.md` to reference the example.
- Add a test in `tests/test_templates.py` that loads templates from this directory via `--pack` behavior.

Acceptance Criteria
- `paperfig templates list --pack examples/template_packs/ai` lists the example template.
- `paperfig templates lint --pack examples/template_packs/ai` passes.
- Tests pass.

