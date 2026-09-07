# Cron Jobs

The FastBrace cron job system is built on **Celery Beat + RedBeat**. Scheduling rules are declared through decorators, and tasks are auto-discovered and registered to Redis, enabling reliable scheduled execution in distributed environments.

## Design Philosophy

### Why RedBeat?

Traditional Celery Beat stores scheduling state in files and does not support multi-instance deployment. RedBeat stores scheduling state in Redis, natively supporting:
- Multi-worker-node deployments with only one active Beat instance
- Persisted scheduling state that survives restarts
- Dynamically adding / modifying / disabling tasks

## Core Code Locations

| File | Responsibility |
|------|----------------|
| `infrastructure/cron/celery_beat.py` | Celery Beat creation and startup |
| `infrastructure/cron/cron_task_config.py` | Task configuration model `RedBeatTaskConfig` |
| `infrastructure/cron/task_loader.py` | Task auto-discovery and registration `TaskManager` |
| `entrance/cron_job.py` | Cron job startup entry point |
| `main.py` | CLI command `server cron_jobs` |

## Configuration

Configure Celery in `infrastructure/config/settings.dev.yaml`:

```yaml
celery:
  result_expires: 86400              # result expiry time (seconds)
  task_serializer: "json"
  result_serializer: "json"
  accept_content: ["json"]
  timezone: "Asia/Shanghai"
  enable_utc: true
  task_acks_late: true               # acknowledge only after the task completes
  task_reject_on_worker_lost: true   # re-dispatch when a worker crashes
  task_publish_retry: true
  task_publish_retry_policy:
    max_retries: 3
    interval_start: 0
    interval_step: 0.5
    interval_max: 3.0
  beat:
    scheduler: "redbeat.RedBeatScheduler"
    beat_max_loop_interval: 30       # max loop interval (seconds)
    beat_sync_every: 5               # sync to Redis every N schedules
    key_prefix: "FastBrace_beat"   # Redis key prefix
    module_path: "application.tasks" # task module scan path
```

## Usage Steps

### Step 1: Create Task Modules

Create task files under `application/tasks/`:

```python
# application/tasks/report_tasks.py
from celery import shared_task
from infrastructure.cron.task_loader import TaskManager

@shared_task
@TaskManager.scheduled(minute="0", hour="2")
def daily_report():
    """Generate the daily report at 2:00 AM every day"""
    # business logic...
    return {"status": "success"}

@shared_task
@TaskManager.scheduled(minute="*/30")
def health_check():
    """Run a health check every 30 minutes"""
    # business logic...
    return {"status": "ok"}
```

### Step 2: Understand the Scheduling Decorator

The parameters of `@TaskManager.scheduled()` map exactly to crontab:

```python
@TaskManager.scheduled(
    minute="0",           # minute (0-59 or *)
    hour="2",             # hour (0-23 or *)
    day_of_week="*",      # day of week (0-6, 0=Monday)
    day_of_month="*",     # day of month (1-31)
    month_of_year="*"     # month of year (1-12)
)
```

Common scheduling rule examples:

| Rule | Meaning |
|------|---------|
| `minute="0", hour="2"` | Every day at 2:00 AM |
| `minute="*/30"` | Every 30 minutes |
| `minute="0", hour="9", day_of_week="1-5"` | 9:00 AM on weekdays |
| `minute="0", hour="0", day_of_month="1"` | 0:00 on the 1st of every month |

### Step 3: Configure the Scan Path

Make sure `module_path` in `settings.yaml` points to the module containing the tasks:

```yaml
celery:
  beat:
    module_path: "application.tasks"
```

`TaskManager` recursively scans all submodules under that module, looking for Celery tasks decorated with `@TaskManager.scheduled()`.

### Step 4: Start the Cron Jobs

```bash
# Start the Beat scheduler (registers tasks and begins scheduling)
python main.py server cron_jobs

# In another terminal, start the worker (executes tasks)
celery -A cron_job worker --loglevel=info
```

Startup flow:
1. `start_cron_job()` initializes logging and module loading
2. `create_celery_beat()` creates the Celery app
3. `TaskManager.register_tasks()` scans and registers all tasks to RedBeat (Redis)
4. `celery_app.Beat().run()` starts the scheduling loop

## Task Auto-Discovery Mechanism

```python
# infrastructure/cron/task_loader.py
class TaskManager:
    @classmethod
    def register_tasks(cls, celery_app, overwrite=True):
        # 1. Load all modules under module_path
        task_configs = cls.load_tasks(celery_app.conf.module_path)
        # 2. Generate RedBeatTaskConfig
        # 3. Register with RedBeat (Redis)
        return cls._register_configs(celery_app, task_configs, overwrite)
```

`load_tasks()` uses `pkgutil.walk_packages()` to recursively scan modules, `inspect.getmembers()` to find `celery.Task` instances, and reads the crontab rules from the decorators.

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Task not executed | Worker not started | Start `celery worker` in another terminal |
| Task executed multiple times | Multiple Beat instances | Ensure only one `cron_jobs` process is running |
| Scheduling not taking effect | Redis connection failure | Check the Redis service and configuration |
| Tasks lost | Redis data cleared | Restart `cron_jobs` to re-register automatically |
