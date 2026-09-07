PYTHON_TARGETS := api application domain entrance event_handlers infrastructure main.py tests
DOC_TARGETS := $(shell find README.md README.en.md docs agent-docs -name '*.md' -type f 2>/dev/null) $(wildcard 模块开发指南.md 需求迭代.md)

# 文档站点命令需要加载 nvm（依赖 bash 环境）
SHELL := /bin/bash
.SHELLFLAGS := -c

.PHONY: lint lint-fix format typecheck test pre-commit layer-style agent-finish docs-dev docs-build docs-preview

# 文档站点命令
define npm_run
	@[ -f $(HOME)/.nvm/nvm.sh ] && . $(HOME)/.nvm/nvm.sh >/dev/null 2>&1 && { nvm use 22 >/dev/null 2>&1 || true; }; cd docs && { command -v npm >/dev/null 2>&1 || { echo "未检测到 Node.js/npm，请先安装（推荐 nvm）"; exit 1; }; } && npm run $(1)
endef

docs-dev:
	$(call npm_run,docs:dev)

docs-build:
	$(call npm_run,docs:build)

docs-preview:
	$(call npm_run,docs:preview)

lint:
	uv run ruff check $(PYTHON_TARGETS)
	uv run mypy $(PYTHON_TARGETS)
	uv run python scripts/check_headers.py
	uv run mdformat --check $(DOC_TARGETS)

lint-fix:
	uv run ruff check --fix $(PYTHON_TARGETS)
	uv run python scripts/check_headers.py --fix
	uv run mdformat $(DOC_TARGETS)

format:
	uv run ruff check --fix $(PYTHON_TARGETS)
	uv run python scripts/check_headers.py --fix

typecheck:
	uv run mypy $(PYTHON_TARGETS)

test:
	uv run pytest

layer-style:
	uv run python scripts/check_headers.py

pre-commit:
	uv run pre-commit run --all-files

agent-finish: lint-fix lint
