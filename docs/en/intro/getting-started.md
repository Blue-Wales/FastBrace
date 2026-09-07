# Quick Start

This page helps you get the FastBrace scaffold running locally in minutes.



## Requirements

- Python 3.10+
- Git (version control)
- [uv](https://docs.astral.sh/uv/) (unified dependency management; if you are new to it, see https://hellowac.github.io/uv-zh-cn/getting-started/installation/)



## Clone the Project

```bash
git clone https://github.com/FastBrace/FastBrace.git
cd FastBrace
```



## Install Dependencies

```bash
# After installing the uv tool

uv sync --all-extras

#  Activate the virtual environment
macOS: source .venv/bin/activate

Windows (cmd or PowerShell): .venv\Scripts\activate

Windows (Git Bash): source .venv/Scripts/activate

```



## Start the Service

```bash
# Start the API service
python main.py server api
```

![Screenshot 2026-08-28 14.48.39](https://picgocloud.com/m/34b9ad28-6a3e-400a-8b1b-bd00f0a34335.png)

## Troubleshooting

### 1. `uv` command not found

**Cause**: uv is not installed, or it was not added to the system PATH after installation.

**Solution**: Install uv first by following the [official uv documentation](https://docs.astral.sh/uv/); after installation, reopen the terminal and run `uv --version` to confirm it is available.

### 2. Python version too low when running `uv sync --all-extras`

**Cause**: FastBrace requires Python 3.10 or above.

**Solution**: Run `python --version` first to confirm the local Python version; if it is too low, upgrade Python, or edit the `.python-version` file in the project root to specify an available version, then run `uv sync --all-extras` again.

### 3. `source .venv/bin/activate` reports that the file or directory does not exist

**Cause**: `uv sync --all-extras` has not been completed successfully yet, so the virtual environment has not been created.

**Solution**: Go back to the project root and run `uv sync --all-extras` first, then activate the virtual environment after the installation succeeds.

### 4. Cannot activate the virtual environment on Windows

**Cause**: The default PowerShell execution policy blocks activation scripts, or the activation command does not match the current terminal type.

**Solution**:
- In cmd or PowerShell, use `.venv\Scripts\activate`
- In Git Bash, use `source .venv/Scripts/activate`
- If PowerShell reports a "running scripts is disabled" error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` first and then retry

### 5. Port already in use when starting the service

**Cause**: The default port (e.g. 8000) is already occupied by another program.

**Solution**: Stop the process occupying the port, or change the port via startup arguments / the configuration file and start again.

### 6. Dependency downloads are slow or fail

**Cause**: Network issues make access to the default package index unstable.

**Solution**: Configure a mirror for uv, e.g. set `[[tool.uv.index]] url = "https://mirrors.aliyun.com/pypi/simple/"` in `pyproject.toml` or `uv.toml` (or another available mirror), then run `uv sync --all-extras` again.

### 7. Dependency conflicts or an inconsistent environment state

**Cause**: Multiple installs, branch switching, and similar operations leave the dependency state inconsistent.

**Solution**: Delete the `.venv` directory and the `uv.lock` file, then run `uv sync --all-extras` again to rebuild the environment.

### 8. `python main.py server api` hangs or errors

**Cause**: The virtual environment is not activated, the command was not run from the project root, or dependencies are not fully installed.

**Solution**: Make sure the virtual environment is activated and you are in the project root, run `uv sync --all-extras` again, then start the service.

## Next Steps

- Learn about the project positioning and core capabilities: [About FastBrace](/en/intro/about)
- Understand the overall layered design: [Architecture Guide](/en/advanced/architecture/domain-layer)
