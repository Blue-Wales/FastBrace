# Scheduled Tasks (Cron Jobs)

FastBrace integrates a scheduled task system based on **Celery Beat + RedBeat**. Scheduling rules are declared with decorators, and tasks are automatically registered to Redis for distributed scheduling.

## Core Concepts

- **Celery Beat**: Celery's scheduled task scheduler, which triggers tasks according to crontab rules
- **RedBeat**: A Redis-backed Celery Beat scheduler that supports persistent task scheduling in distributed environments
- **Task configuration**: Tasks are defined with the `RedBeatTaskConfig` model, including the task path, crontab rule, and enabled flag
- **Auto-discovery**: `TaskManager` automatically scans all Celery tasks in the specified module, reads the scheduling rules from their decorators, and registers them
- **Decorator-based scheduling**: Declare crontab rules on task functions with the `@TaskManager.scheduled()` decorator

## File Locations

| File | Description |
|------|------|
| `infrastructure/cron/celery_beat.py` | Celery Beat creation and startup |
| `infrastructure/cron/cron_task_config.py` | Scheduled task configuration model (RedBeatTaskConfig) |
| `infrastructure/cron/task_loader.py` | Task auto-discovery and registration (TaskManager) |
| `entrance/cron_job.py` | Scheduled task startup entry point |
| `main.py` | CLI command `server cron_jobs` |

## Usage

### 1. Define a Scheduled Task

Create a Celery task in your task module and declare its schedule with `@TaskManager.scheduled()`:

```python
from celery import Celery
from infrastructure.cron.task_loader import TaskManager

celery_app = Celery()

@celery_app.task
@TaskManager.scheduled(minute="0", hour="2")
def daily_report():
    """Generate the daily report at 2:00 AM every day"""
    ...
```

### 2. Start Scheduled Tasks

> [!NOTE]
>
> ⚠️: The event service also needs to be enabled. Run:
>
> ```
> python main.py server events
> ```
>
>

```bash
python main.py server cron_jobs
```

Once started, `TaskManager` automatically scans all Celery tasks under `module_path`, reads the crontab rules from the `@TaskManager.scheduled()` decorators, and registers them with RedBeat (Redis).

### crontab Parameters

| Parameter | Description | Default |
|------|------|--------|
| `minute` | Minute (0-59 or `*`) | `*` |
| `hour` | Hour (0-23 or `*`) | `*` |
| `day_of_week` | Day of week (0-6, 0=Monday) | `*` |
| `day_of_month` | Day of month (1-31) | `*` |
| `month_of_year` | Month (1-12) | `*` |

## Common Business Scenarios

The following scenarios benefit from scheduled tasks:

- **Scheduled reports**: generate and push daily/weekly reports at a fixed time each day, e.g. `daily_report`
- **Periodic data cleanup**: periodically clean up expired sessions, temporary files, logs, and other redundant data to avoid storage bloat
- **Scheduled data sync**: periodically pull or sync data from third-party systems to keep local data up to date
- **Business reminders**: periodically scan expiring, overdue, or pending business data and trigger reminder notifications
