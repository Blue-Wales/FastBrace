# 定时任务

FastBrace 定时任务系统基于 **Celery Beat + RedBeat** 构建，支持通过装饰器声明调度规则，任务自动发现并注册到 Redis，实现分布式环境下的可靠定时调度。



## 设计思想



### 为什么选择 RedBeat？

传统 Celery Beat 使用文件存储调度状态，不支持多实例部署。RedBeat 将调度状态存储在 Redis 中，天然支持：
- 多 Worker 节点部署，只有一个 Beat 实例活跃
- 任务调度状态持久化，重启不丢失
- 动态添加/修改/禁用任务

## 核心代码位置

| 文件 | 职责 |
|------|------|
| `infrastructure/cron/celery_beat.py` | Celery Beat 创建与启动 |
| `infrastructure/cron/cron_task_config.py` | 任务配置模型 `RedBeatTaskConfig` |
| `infrastructure/cron/task_loader.py` | 任务自动发现与注册 `TaskManager` |
| `entrance/cron_job.py` | 定时任务启动入口 |
| `main.py` | CLI 命令 `server cron_jobs` |

## 配置

在 `infrastructure/config/settings.dev.yaml` 中配置 Celery：

```yaml
celery:
  result_expires: 86400              # 结果过期时间（秒）
  task_serializer: "json"
  result_serializer: "json"
  accept_content: ["json"]
  timezone: "Asia/Shanghai"
  enable_utc: true
  task_acks_late: true               # 任务完成后才确认
  task_reject_on_worker_lost: true   # Worker 崩溃时重新派发
  task_publish_retry: true
  task_publish_retry_policy:
    max_retries: 3
    interval_start: 0
    interval_step: 0.5
    interval_max: 3.0
  beat:
    scheduler: "redbeat.RedBeatScheduler"
    beat_max_loop_interval: 30       # 最大循环间隔（秒）
    beat_sync_every: 5               # 每 N 次调度后同步到 Redis
    key_prefix: "FastBrace_beat"   # Redis key 前缀
    module_path: "application.tasks" # 任务模块扫描路径
```

## 使用步骤

### 第一步：创建任务模块

在 `application/tasks/` 下创建任务文件：

```python
# application/tasks/report_tasks.py
from celery import shared_task
from infrastructure.cron.task_loader import TaskManager

@shared_task
@TaskManager.scheduled(minute="0", hour="2")
def daily_report():
    """每天凌晨 2:00 生成日报"""
    # 业务逻辑...
    return {"status": "success"}

@shared_task
@TaskManager.scheduled(minute="*/30")
def health_check():
    """每 30 分钟执行一次健康检查"""
    # 业务逻辑...
    return {"status": "ok"}
```

### 第二步：理解调度装饰器

`@TaskManager.scheduled()` 的参数与 crontab 完全对应：

```python
@TaskManager.scheduled(
    minute="0",           # 分钟（0-59 或 *）
    hour="2",             # 小时（0-23 或 *）
    day_of_week="*",      # 星期（0-6，0=周一）
    day_of_month="*",     # 日期（1-31）
    month_of_year="*"     # 月份（1-12）
)
```

常用调度规则示例：

| 规则 | 含义 |
|------|------|
| `minute="0", hour="2"` | 每天凌晨 2:00 |
| `minute="*/30"` | 每 30 分钟 |
| `minute="0", hour="9", day_of_week="1-5"` | 工作日每天 9:00 |
| `minute="0", hour="0", day_of_month="1"` | 每月 1 号 0:00 |

### 第三步：配置扫描路径

确保 `settings.yaml` 中的 `module_path` 指向任务所在模块：

```yaml
celery:
  beat:
    module_path: "application.tasks"
```

`TaskManager` 会递归扫描该模块下所有子模块，查找带有 `@TaskManager.scheduled()` 装饰器的 Celery Task。

### 第四步：启动定时任务

```bash
# 启动 Beat 调度器（注册任务并开始调度）
python main.py server cron_jobs

# 另开终端启动 Worker（执行任务）
celery -A cron_job worker --loglevel=info
```

启动流程：
1. `start_cron_job()` 初始化日志和模块加载
2. `create_celery_beat()` 创建 Celery 应用
3. `TaskManager.register_tasks()` 扫描并注册所有任务到 RedBeat（Redis）
4. `celery_app.Beat().run()` 启动调度循环

## 任务自动发现机制

```python
# infrastructure/cron/task_loader.py
class TaskManager:
    @classmethod
    def register_tasks(cls, celery_app, overwrite=True):
        # 1. 加载 module_path 下所有模块
        task_configs = cls.load_tasks(celery_app.conf.module_path)
        # 2. 生成 RedBeatTaskConfig
        # 3. 注册到 RedBeat（Redis）
        return cls._register_configs(celery_app, task_configs, overwrite)
```

`load_tasks()` 使用 `pkgutil.walk_packages()` 递归扫描模块，通过 `inspect.getmembers()` 查找 `celery.Task` 实例，从装饰器中读取 crontab 规则。

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 任务未执行 | Worker 未启动 | 另开终端启动 `celery worker` |
| 任务重复执行 | 多个 Beat 实例 | 确保只有一个 `cron_jobs` 进程运行 |
| 调度不生效 | Redis 连接失败 | 检查 Redis 服务和配置 |
| 任务丢失 | Redis 数据清除 | 重启 `cron_jobs` 自动重新注册 |
