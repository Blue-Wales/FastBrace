# 工程化工具



## 工程化工具链

| 工具           | 作用                                    | 配置位置                     |
| -------------- | --------------------------------------- | ---------------------------- |
| uv             | 依赖与虚拟环境管理                      | `pyproject.toml` / `uv.lock` |
| Ruff           | Python 静态检查、导入排序               | `pyproject.toml`             |
| mypy           | Python 类型检查                         | `pyproject.toml`             |
| 分层风格检查   | 分层文件头与书写风格约定                | `scripts/check_headers.py`   |
| pytest         | 单元测试与异步接口测试                  | `pyproject.toml`             |
| pytest-asyncio | 异步测试支持                            | `pyproject.toml`             |
| httpx          | 接口测试客户端                          | `pyproject.toml`             |
| mdformat       | Markdown 文档格式校验                   | `pyproject.toml`             |
| Makefile       | 一键执行脚本入口（lint、test、docs 等） | `Makefile`                   |
| Docker/Compose | 容器化部署                              | `deploy/`                    |
| GitHub Actions | CI/CD 流水线                            | `.github/workflows/`         |



## 一键命令

```bash
# 安装开发依赖
uv sync --extra dev

# 检查代码、类型和文档
make lint

# 自动修复可修复问题
make lint-fix

# 自动修复静态检查问题
make format

# 仅执行类型检查
make typecheck

# 仅检查分层文件头与书写风格
make layer-style

# 安装并运行提交前检查
uv run pre-commit install
make pre-commit
```



`make lint-fix` 会自动执行 Ruff 静态修复、分层文件头日期更新和 Markdown 格式化。无法自动修复的规则仍需按命令输出手动调整。

