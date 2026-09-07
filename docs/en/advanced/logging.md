# Logging System

The FastBrace logging system is built on **Loguru** and managed uniformly through a singleton `LoggerManager`. It supports per-process independent logs, automatic rotation, asynchronous writing, and signal-based runtime control — production-grade features throughout.

## Design Philosophy

### Independent Logs per Module

The framework configures a separate log channel for each of the three core processes:

| Process | Log Config | Log Directory |
|---------|------------|---------------|
| API service | `api_log` | `logs/FastBrace/api/` |
| Event bus | `event_log` | `logs/FastBrace/event/` |
| Cron jobs | `cron_log` | `logs/FastBrace/cron/` |

Each channel independently writes two log files:
- `{name}.log`: full logs (DEBUG/INFO/WARNING/ERROR)
- `{name}_error.log`: WARNING and above only

### Asynchronous Logging Strategy

Production environments automatically enable the asynchronous log queue (`enqueue=True`); log writes are handled by a background thread and never block business threads. Development environments use synchronous mode for easier debugging.

## Configuration

Configure each module's logs in `infrastructure/config/settings.dev.yaml`:

```yaml
api_log:
  log_dir: 'logs/FastBrace/api'
  log_name: 'api'
  debug: false                  # whether DEBUG level is enabled by default
  log_rotation: "200 MB"        # rotate when a single file reaches this size
  log_retention: 5              # keep at most 5 rotated files
  error_log_rotation: "100 MB"
  error_log_retention: 3
  use_async_logging: true       # whether to use the async log queue

event_log:
  log_dir: 'logs/FastBrace/event'
  log_name: 'event'
  # ... same as above

cron_log:
  log_dir: 'logs/FastBrace/cron'
  log_name: 'cron'
  # ... same as above
```

**Configuration options:**

| Option | Description | Default |
|--------|-------------|---------|
| `log_dir` | Log file output directory | - |
| `log_name` | Log file name prefix | - |
| `debug` | Whether DEBUG level is enabled | `false` |
| `log_rotation` | Main log rotation threshold (size or time based) | `"200 MB"` |
| `log_retention` | Number of main log files to keep | `5` |
| `error_log_rotation` | Error log rotation threshold | `"100 MB"` |
| `error_log_retention` | Number of error log files to keep | `3` |
| `use_async_logging` | Whether to use the async queue | `false` |

## Usage

### Using the Logger in Code

The framework exports a global `logger` instance; use it directly in business code:

```python
from loguru import logger

logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
```

Log format:

```
2026-08-29 10:30:00 | INFO     | system | api.user:get_users:42 | 获取用户列表成功
Time               | Level    | ReqID  | Module:Function:Line  | Message
```

> File logs now use `serialize=True`, so each record is written to disk as a **single-line JSON** (the format above is the readable `text` field, both in JSON and on the console), making them easy to collect and query. See [Log Monitoring](./log-monitoring.md).

### Dynamically Switching Log Levels

**Option 1: environment variable (at startup)**

```bash
LOG_DEBUG=true python main.py server api
```

**Option 2: Unix signals (at runtime)**

```bash
# Toggle DEBUG/INFO level
kill -USR1 <pid>

# Inspect the current log status
kill -USR2 <pid>
```

Signal handling is only available on Unix; `LoggerManager` automatically registers `SIGUSR1` and `SIGUSR2` handlers at initialization.

## Log Rotation and Compression

- Old log files are automatically compressed with `tar.gz` to save disk space
- Rotation triggers automatically when the `log_rotation` threshold is reached, producing a new timestamped file
- Old files beyond the `log_retention` count are deleted automatically

## Adding a New Log Module

1. Add the new module to the `ModulesForLogger` enum in `infrastructure/core/log.py`:

```python
class ModulesForLogger(Enum):
    API = "api_log"
    EVENT_BUS = "event_log"
    CRON_JOB = "cron_log"
    NEW_MODULE = "new_log"  # new
```

2. Add the corresponding log configuration in `settings.yaml`:

```yaml
new_log:
  log_dir: 'logs/FastBrace/new'
  log_name: 'new'
  # ...
```

3. Call `init_logger(ModulesForLogger.NEW_MODULE)` in the startup entry point
