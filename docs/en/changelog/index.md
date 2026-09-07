# Changelog

Records the version iterations and important changes of FastBrace.

## 1.0.0

`2026-08-22`

First public release.

### Added

- DDD four-layer architecture: `api/`, `application/`, `domain/`, `infrastructure/`, with built-in inter-layer dependency rule checks
- Built-in backend features: users, roles, permissions, file upload, and login authentication
- Celery async tasks, event bus, and scheduled job support
- Engineering quality toolchain: Ruff + mypy + pytest + pre-commit + GitHub Actions CI
- Docker + docker-compose one-click deployment
- `agent-docs/` development constraints and conventions for AI agents
- VitePress-based documentation site with Chinese/English switching
