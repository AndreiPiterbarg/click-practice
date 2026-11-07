---
name: add-tests
description: Use when asked to add tests for an existing function or class with little or no direct coverage. Not for fixing bugs or changing library code.
---

# Add tests

Repo conventions live in `AGENTS.md`; follow them. This is the procedure.

1. Understand the code: read the target function/class and its upstream
   callers and downstream dependencies.
2. Search for existing tests, both the mirror test file
   (`tests/test_<module>.py`) and indirect coverage via higher-level tests.
   Check `tests/conftest.py` for existing fixtures before adding new ones.
3. Put new tests in the most appropriate file, matching current style (one
   import per line, `import typing as t`, no ternaries, no silenced warnings).
4. Test each specific behaviour, including edge cases and error paths.
5. Sanity-check the tests are real: they should fail if the target code is
   broken or removed.
6. If testing reveals a bug, report it. Do not fix library code in this PR.
7. Run `uv run pytest` (stress tests stay deselected),
   `uv run ruff check --no-fix .`, `uv run ruff format --check .`, and
   `uv run pre-commit run --all-files`.
8. If all pass, open a PR. Test-only changes need no CHANGES.md entry.
