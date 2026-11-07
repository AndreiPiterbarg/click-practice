# AGENTS.md

## Commands
- Install: `uv sync --locked`
- Tests: `uv run pytest` (stress tests are deselected by default; leave them off
  unless touching CliRunner or stream code)
- Lint: `uv run ruff check --no-fix .` and `uv run ruff format --check .`. Ruff
  is configured with `fix = true`, so a plain `ruff check` rewrites files.
- Types: `uv run mypy` and `uv run pyright --ignoreexternal --verifytypes click`
- Before opening a PR: `uv run pre-commit run --all-files` (CI runs the same)

## Conventions
- One import per line (isort force-single-line); `typing` is imported as `t`.
- No ternary expressions; coverage can't measure both branches. Use if/else.
- No new dependencies when the standard library works.
- Warnings are errors in tests (`filterwarnings = error`). Don't silence them.
- Wrap Markdown at 80 columns.
- When `make_pass_decorator` cannot find the object, the RuntimeError it raises
  should suggest passing `ensure=True`.

## Changes
- User-visible changes need an entry in CHANGES.md (top unreleased version,
  linked with {pr}`N`) and a `.. versionchanged::` or `.. versionadded::` note
  in the docstring. Test-only changes need neither.
- The PR template mentions CHANGES.rst and CONTRIBUTING.rst. Those files don't
  exist: use CHANGES.md and docs/contributing.md.
- Tests must fail without the change.

## Layout
- Library code in src/click/; tests in tests/ mirroring the modules; typing
  tests in tests/typing/.
