# 日志系统

FastBrace 日志系统基于 **Loguru** 构建，采用单例模式的 `LoggerManager` 统一管理，支持多进程独立日志、自动轮转、异步写入、信号动态调控等生产级特性。

## 设计思想

### 多模块独立日志

框架为三个核心进程分别配置独立的日志通道：

| 进程 | 日志配置 | 日志目录 |
|------|----------|----------|
| API 服务 | `api_log` | `logs/FastBrace/api/` |
| 事件总线 | `event_log` | `logs/FastBrace/event/` |
| 定时任务 | `cron_log` | `logs/FastBrace/cron/` |

每个通道独立输出两个日志文件：
- `{name}.log`：全量日志（DEBUG/INFO/WARNING/ERROR）
- `{name}_error.log`：仅 WARNING 及以上级别



### 异步日志策略

生产环境自动启用异步日志队列（`enqueue=True`），日志写入由后台线程处理，不阻塞业务线程。开发环境使用同步模式，便于调试。



## 配置

在 `infrastructure/config/settings.dev.yaml` 中配置各模块日志：

```yaml
api_log:
  log_dir: 'logs/FastBrace/api'
  log_name: 'api'
  debug: false                  # 是否默认开启 DEBUG 级别
  log_rotation: "200 MB"        # 单文件达到此大小后轮转
  log_retention: 5              # 最多保留 5 个轮转文件
  error_log_rotation: "100 MB"
  error_log_retention: 3
  use_async_logging: true       # 是否使用异步日志队列

event_log:
  log_dir: 'logs/FastBrace/event'
  log_name: 'event'
  # ... 同上

cron_log:
  log_dir: 'logs/FastBrace/cron'
  log_name: 'cron'
  # ... 同上
```

**配置项说明：**

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `log_dir` | 日志文件输出目录 | - |
| `log_name` | 日志文件名前缀 | - |
| `debug` | 是否开启 DEBUG 级别 | `false` |
| `log_rotation` | 主日志轮转阈值（按大小或时间） | `"200 MB"` |
| `log_retention` | 主日志保留文件数 | `5` |
| `error_log_rotation` | 错误日志轮转阈值 | `"100 MB"` |
| `error_log_retention` | 错误日志保留文件数 | `3` |
| `use_async_logging` | 是否使用异步队列 | `false` |

## 使用方式

### 在代码中使用日志

框架全局导出了 `logger` 实例，直接在业务代码中使用：

```python
from loguru import logger

logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
```

日志格式：

```
2026-08-29 10:30:00 | INFO     | system | api.user:get_users:42 | 获取用户列表成功
时间               | 级别     | 请求ID | 模块:函数:行号          | 消息
```

> 文件日志已启用 `serialize=True`，每条记录以**单行 JSON** 落盘（上述为控制台及 JSON 中 `text` 字段的可读格式），便于结构化采集与检索，详见[线上日志查看](./log-monitoring.md)。

### 动态切换日志级别

**方式一：环境变量（启动时）**

```bash
LOG_DEBUG=true python main.py server api
```

**方式二：Unix 信号（运行时）**

```bash
# 切换 DEBUG/INFO 级别
kill -USR1 <pid>

# 查看当前日志状态
kill -USR2 <pid>
```

信号处理仅在 Unix 系统下可用，`LoggerManager` 在初始化时自动注册 `SIGUSR1` 和 `SIGUSR2` 信号处理器。

## 日志轮转与压缩

- 旧日志文件自动使用 `tar.gz` 压缩，节省磁盘空间
- 达到 `log_rotation` 阈值后自动轮转，生成带时间戳的新文件
- 超过 `log_retention` 数量的旧文件自动删除

## 添加新的日志模块

1. 在 `infrastructure/core/log.py` 的 `ModulesForLogger` 枚举中添加新模块：

```python
class ModulesForLogger(Enum):
    API = "api_log"
    EVENT_BUS = "event_log"
    CRON_JOB = "cron_log"
    NEW_MODULE = "new_log"  # 新增
```

2. 在 `settings.yaml` 中添加对应的日志配置：

```yaml
new_log:
  log_dir: 'logs/FastBrace/new'
  log_name: 'new'
  # ...
```

3. 在启动入口调用 `init_logger(ModulesForLogger.NEW_MODULE)`
