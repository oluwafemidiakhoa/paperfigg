Title: Add architecture critique rule for zero-traceability figures
Labels: good first issue

Body:
Goal
Flag runs where any figure has zero traceability coverage.

Scope
- Add a rule module in `paperfig/critique/rules/` (e.g., `zero_traceability.py`).
- Register it in `paperfig/critique/rules/__init__.py`.
- Use `inspect.json` per-figure traceability coverage to identify figures with `coverage == 0` or `None`.
- Add a test in `tests/test_architecture_critic.py` that enables only this rule and verifies the finding.

Acceptance Criteria
- `paperfig critique-architecture --list-rules` includes the new rule.
- The rule emits a finding with a clear suggestion and evidence.
- Tests pass.

