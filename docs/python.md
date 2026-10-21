# Python Development Standards

Choices another competent Python dev would make differently. Everything not
listed here follows normal modern Python practice.

## Tooling

- `uv` for package management. Not pip, not poetry, not conda.
- Virtual environments local to the project directory. Never install project
  dependencies into a global Python.
- `ruff` for linting and formatting. Not flake8 plus black.
- `pyright` for static type analysis. Not mypy.
- `pytest`, with pytest-asyncio for async tests.

## Frameworks

- Standalone services and APIs: FastAPI.
- The ORM follows the framework. Django ORM inside Django, SQLAlchemy inside
  FastAPI. Do not mix them in one project.

## Typing

- Annotate all new function signatures, parameters and return types.
- `X | None` (PEP 604), never `Optional[X]`.
- When pyright false-positives, silence it narrowly with the specific rule,
  such as `# type: ignore[reportAttributeAccessIssue]`, plus a brief comment
  saying why. Not a bare `# type: ignore`.

## Layout

`src/` layout: package under `src/<project_name>/`, tests in a sibling `tests/`
directory, config in `pyproject.toml`.
