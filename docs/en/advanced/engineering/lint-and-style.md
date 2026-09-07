# Engineering Tooling



## Toolchain

| Tool           | Role                                                    | Configuration                |
| -------------- | ------------------------------------------------------- | ---------------------------- |
| uv             | Dependency and virtual environment management           | `pyproject.toml` / `uv.lock` |
| Ruff           | Python static checks, import sorting                    | `pyproject.toml`             |
| mypy           | Python type checking                                    | `pyproject.toml`             |
| Layer-style check | Layered file headers and writing-style conventions   | `scripts/check_headers.py`   |
| pytest         | Unit tests and async API tests                          | `pyproject.toml`             |
| pytest-asyncio | Async test support                                      | `pyproject.toml`             |
| httpx          | API test client                                         | `pyproject.toml`             |
| mdformat       | Markdown documentation format validation                | `pyproject.toml`             |
| Makefile       | One-stop script entry (lint, test, docs, etc.)          | `Makefile`                   |
| Docker/Compose | Containerized deployment                                | `deploy/`                    |
| GitHub Actions | CI/CD pipeline                                          | `.github/workflows/`         |



## One-Command Workflows

```bash
# Install dev dependencies
uv sync --extra dev

# Check code, types, and docs
make lint

# Auto-fix fixable issues
make lint-fix

# Auto-fix static check issues
make format

# Run type checks only
make typecheck

# Check layered file headers and writing style only
make layer-style

# Install and run pre-commit checks
uv run pre-commit install
make pre-commit
```



`make lint-fix` automatically runs Ruff static fixes, layered file header date updates, and Markdown formatting. Rules that cannot be auto-fixed still require manual adjustment based on the command output.
