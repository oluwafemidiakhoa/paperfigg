Title: Add Windows PNG doctor verification test
Labels: good first issue

Body:
Goal
Add unit test coverage for Windows-specific PNG guidance output.

Scope
- Update `tests/test_cli_extensions.py` to patch `platform.system()` as "Windows".
- Ensure `paperfig doctor --fix png` output includes both MSYS2 and Conda commands.

Acceptance Criteria
- The test verifies presence of MSYS2 and Conda guidance strings.
- Tests pass on CI.

