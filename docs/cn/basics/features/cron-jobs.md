# 定时任务

FastBrace 集成了基于 **Celery Beat + RedBeat** 的定时任务系统，支持通过装饰器声明调度规则，任务自动注册到 Redis 进行分布式调度。



## 核心概念

- **Celery Beat**：Celery 的定时任务调度器，按 crontab 规则触发任务
- **RedBeat**：基于 Redis 的 Celery Beat 调度器，支持分布式环境下的任务调度持久化
- **任务配置**：使用 `RedBeatTaskConfig` 模型定义任务，包含任务路径、crontab 规则、是否启用等
- **自动发现**：`TaskManager` 自动扫描指定模块下的所有 Celery Task，读取装饰器中的调度规则并注册
- **装饰器调度**：使用 `@TaskManager.scheduled()` 装饰器在任务函数上声明 crontab 规则



## 文件位置

| 文件 | 说明 |
|------|------|
| `infrastructure/cron/celery_beat.py` | Celery Beat 创建与启动 |
| `infrastructure/cron/cron_task_config.py` | 定时任务配置模型 |
| `infrastructure/cron/task_loader.py` | 任务自动发现与注册 |
| `entrance/cron_job.py` | 定时任务启动入口 |
| `main.py` | CLI 命令 `server cron_jobs` |



## 使用方式

### 1. 定义定时任务

在任务模块中创建 Celery Task，使用 `@TaskManager.scheduled()` 声明调度规则：

```python
from celery import Celery
from infrastructure.cron.task_loader import TaskManager

celery_app = Celery()

@celery_app.task
@TaskManager.scheduled(minute="0", hour="2")
def daily_report():
    """每天凌晨 2 点执行日报生成"""
    ...
```



### 2. 启动定时任务

> [!NOTE]
>
> ⚠️： 需要同时启用事件服务，执行命令
>
> ```
> python main.py server events
> ```
>
> 



```bash
python main.py server cron_jobs
```

启动后，`TaskManager` 会自动扫描 `module_path` 下的所有 Celery Task，读取 `@TaskManager.scheduled()` 装饰器中的 crontab 规则，并注册到 RedBeat（Redis）。



### crontab 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `minute` | 分钟（0-59 或 `*`） | `*` |
| `hour` | 小时（0-23 或 `*`） | `*` |
| `day_of_week` | 星期（0-6，0=周一） | `*` |
| `day_of_month` | 日期（1-31） | `*` |
| `month_of_year` | 月份（1-12） | `*` |

## 常见业务场景

以下业务场景适合使用定时任务：

- **每日定时报表**：每天在固定时间生成并推送日报/周报，如 `daily_report`
- **定期数据清理**：定时清理过期会话、临时文件、日志等冗余数据，避免存储膨胀
- **定时数据同步**：周期性从第三方系统拉取或同步数据，保持本地数据最新
- **业务提醒**：定时扫描到期、待办等业务数据，触发提醒通知
