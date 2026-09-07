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

**简体中文** | [English](./README.en.md)

</div>

## 介绍

FastBrace是一个基于Python**高性能异步框架Fastapi构建的轻量级脚手架**，目标是为开发企业级后台管理项目提供开箱即用的解决方案， 帮助你快速、高效的完成企业级高性能接口开发

## 文档说明



本地启动文档开发服务器：

```bash
cd docs && npm install && npm run docs:dev
```



详见 [文档站开发与部署](https://docs.FastBrace.dev/basics/docs-dev-deploy)。

## 快速开始

### 环境要求

- Python 3.10+
- MySQL 8.x
- Redis 6+
- uv

### 安装依赖

```bash
uv sync --all-extras
```

如果当前环境尚未安装 uv：

```bash
pip install uv
```

### 启动 API

```bash
uv run python main.py server api
```

访问：

- Swagger: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Health Check: `http://127.0.0.1:8000/health`

### 启动事件总线

```bash
uv run python main.py server events
```

### 启动定时任务

```bash
uv run python main.py server cron_jobs
```

## License

[MIT](LICENSE)

## 贡献

欢迎提交 Issue 和 Pull Request。建议贡献前先运行：

```bash
make agent-finish
make test
```
