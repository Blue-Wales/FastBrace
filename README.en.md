# FastBrace

<p align="center">
  <img src="assets/FastBrace.png" alt="FastBrace" width="820" />
</p>

<p align="center">
  <em>FastBrace is a lightweight and high-performance scaffolding framework built based on Fastapi.</em>
</p>
<p align="center">
  <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white"></a>
  <a href="https://fastapi.tiangolo.com/"><img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.109%2B-009688?logo=fastapi&logoColor=white"></a>
  <a href="https://docs.astral.sh/uv/"><img alt="uv" src="https://img.shields.io/badge/uv-ready-111827"></a>
</p>
<p align="center">
  <img alt="Architecture" src="https://img.shields.io/badge/architecture-DDD-2563EB">
  <img alt="API Docs" src="https://img.shields.io/badge/API-OpenAPI%20%7C%20Swagger-85EA2D?logo=swagger&logoColor=111827">
  <img alt="Database" src="https://img.shields.io/badge/database-MySQL-4479A1?logo=mysql&logoColor=white">
  <img alt="Container" src="https://img.shields.io/badge/container-Docker-2496ED?logo=docker&logoColor=white">
</p>

<div align="center">

[简体中文](./README.md) | **English**

</div>

## Introduction

FastBrace is a **lightweight scaffolding built on FastAPI, Python's high-performance asynchronous framework**. It aims to provide an out-of-the-box solution for developing enterprise-level admin projects, helping you quickly and efficiently build high-performance enterprise APIs.

## Documentation

Start the local docs dev server:

```bash
cd docs && npm install && npm run docs:dev
```

See [Docs Dev & Deploy](https://docs.FastBrace.dev/basics/docs-dev-deploy) for details.

## Quick Start

### Requirements

- Python 3.10+
- MySQL 8.x
- Redis 6+
- uv

### Install Dependencies

```bash
uv sync --all-extras
```

If uv is not installed yet:

```bash
pip install uv
```

### Start API

```bash
uv run python main.py server api
```

Open:

- Swagger: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Health Check: `http://127.0.0.1:8000/health`

### Start Event Bus

```bash
uv run python main.py server events
```

### Start Scheduled Jobs

```bash
uv run python main.py server cron_jobs
```

## License

[MIT](LICENSE)

## Contributing

Issues and pull requests are welcome. Before contributing, run:

```bash
make agent-finish
make test
```
