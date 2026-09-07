# 快速开始

本页帮助你在本地快速运行 FastBrace 脚手架。



## 环境要求

- Python 3.10+
- Git (版本控制)
- [uv](https://docs.astral.sh/uv/)（统一依赖管理，不熟悉可查看 https://hellowac.github.io/uv-zh-cn/getting-started/installation/）



## 克隆项目

```bash
git clone https://github.com/FastBrace/FastBrace.git
cd FastBrace
```



## 安装依赖

```bash
# 下载安装好uv工具后

uv sync --all-extras

#  加载虚拟环境
mac电脑： source .venv/bin/activate

windows电脑（cmd 或 PowerShell）： .venv\Scripts\activate

windows电脑（Git Bash）： source .venv/Scripts/activate

```



## 启动服务

```bash
# 启动 API 服务
python main.py server api
```



## 常见问题

### 1. 提示 `uv` 命令找不到

**原因**：未安装 uv，或安装后未将其加入系统 PATH。

**解决**：先到 [uv 官方文档](https://docs.astral.sh/uv/) 完成安装；安装后重新打开终端，执行 `uv --version` 确认可用。

### 2. 执行 `uv sync --all-extras` 时报 Python 版本过低

**原因**：FastBrace 要求 Python 3.10 及以上版本。

**解决**：先执行 `python --version` 确认本机 Python 版本；如版本过低，请升级 Python，或修改项目根目录 `.python-version` 文件指定一个可用的版本后重新执行 `uv sync --all-extras`。

### 3. `source .venv/bin/activate` 提示文件或目录不存在

**原因**：尚未成功执行 `uv sync --all-extras`，虚拟环境还没有生成。

**解决**：先回到项目根目录执行 `uv sync --all-extras`，安装成功后再加载虚拟环境。

### 4. Windows 下无法激活虚拟环境

**原因**：PowerShell 默认执行策略禁止运行激活脚本，或激活命令与当前终端类型不匹配。

**解决**：
- cmd 或 PowerShell 使用 `.venv\Scripts\activate`
- Git Bash 使用 `source .venv/Scripts/activate`
- 若 PowerShell 报「禁止运行脚本」错误，先执行 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` 后重试

### 5. 启动服务时报端口被占用

**原因**：默认端口（如 8000）已被其他程序占用。

**解决**：结束占用该端口的进程，或通过启动参数 / 配置文件更换端口后重新启动。

### 6. 依赖下载缓慢或失败

**原因**：网络原因导致访问默认包源不稳定。

**解决**：为 uv 配置镜像源，例如在 `pyproject.toml` 或 `uv.toml` 中配置 `[[tool.uv.index]] url = "https://mirrors.aliyun.com/pypi/simple/"`（或其他可用镜像），然后重新执行 `uv sync --all-extras`。

### 7. 依赖冲突或环境状态异常

**原因**：多次安装、切换分支等原因导致依赖状态不一致。

**解决**：删除 `.venv` 目录与 `uv.lock` 文件后，重新执行 `uv sync --all-extras` 重建环境。

### 8. 执行 `python main.py server api` 无响应或报错

**原因**：未加载虚拟环境、未在项目根目录执行，或依赖未完整安装。

**解决**：确认已激活虚拟环境并位于项目根目录，重新执行 `uv sync --all-extras` 后再启动服务。

## 下一步

- 了解项目定位与核心能力：[项目简介](/intro/about)
- 了解整体分层设计：[架构指南](/advanced/architecture/domain-layer)
