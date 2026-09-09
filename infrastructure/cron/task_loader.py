#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : task_loader.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

# infrastructure/cron/task_manager.py

import importlib
import inspect
import pkgutil
from collections.abc import Callable
from functools import wraps

from celery import Task
from celery.schedules import crontab
from loguru import logger
from redbeat import RedBeatSchedulerEntry

from infrastructure.cron.cron_task_config import RedBeatTaskConfig


class TaskManager:
    @classmethod
    def scheduled(cls, minute="*", hour="*", day_of_week="*", day_of_month="*", month_of_year="*"):
        """
        装饰器：用于在 Celery Task 上设置调度规则
        示例：
            @shared_task
            @TaskManager.scheduled(minute="30", hour="2")
            def daily_report():
                ...
        """
        def decorator(func: Callable):
            """添加任务调度规则"""
            func.schedule = crontab(
                minute=minute,
                hour=hour,
                day_of_week=day_of_week,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
            )

            @wraps(func)
            def wrapper(*args, **kwargs_func):
                return func(*args, **kwargs_func)

            return wrapper

        return decorator

    @classmethod
    def create_config(cls, task, enabled: bool = True) -> RedBeatTaskConfig:
        """
        根据 Celery Task 函数动态创建 RedBeatTaskConfig
        支持从装饰器中读取调度规则
        """
        module_path = f"{task.__module__}.{task.__name__}"
        # 获取调度规则
        schedule = getattr(task.__wrapped__, "schedule", {})
        return RedBeatTaskConfig(
            name=task.__name__, task=module_path, cron=schedule, enabled=enabled
        )

    @classmethod
    def load_tasks(cls, package_path: str) -> list[RedBeatTaskConfig]:
        """
        加载指定模块下的所有 Celery Task 并生成配置
        """
        try:
            # 导入主模块
            package = importlib.import_module(package_path)
            logger.info(f"成功导入主模块: {package_path}")

            tasks = []

            for _, module_name, _ in pkgutil.walk_packages(
                package.__path__, package.__name__ + "."
            ):
                logger.debug(f"正在扫描模块: {module_name}")
                try:
                    module = importlib.import_module(module_name)
                    tasks.extend(cls._load_tasks_from_module(module))
                except Exception as e:
                    logger.error(f"模块 {module_name} 加载失败: {e}")

            return tasks

        except ImportError as e:
            logger.error(f"模块 {package_path} 导入失败: {e}")
            return []

    @classmethod
    def _load_tasks_from_module(cls, module) -> list[RedBeatTaskConfig]:
        sub_tasks = []
        for name, value in inspect.getmembers(module):
            if isinstance(value, Task):
                try:
                    config = cls.create_config(value)
                    sub_tasks.append(config)
                    logger.info(f"发现 Celery Task: {value.__name__}")
                except Exception as e:
                    logger.error(f"创建任务配置失败: {name}: {e}")
                    continue
        return sub_tasks

    @classmethod
    def register_tasks(cls, celery_app, overwrite: bool = True) -> list[str]:
        """
        加载并注册任务到 RedBeat（Celery Beat Redis 调度器）
        """
        task_configs = cls.load_tasks(celery_app.conf.module_path)
        return cls._register_configs(celery_app, task_configs, overwrite)

    @classmethod
    def _register_configs(cls, celery_app, task_configs, overwrite=True) -> list[str]:
        """
        将 RedBeatTaskConfig 列表注册到 RedBeat（Celery Beat Redis 调度器）
        """
        loaded_tasks = []

        for config in task_configs:
            if not config.enabled:
                logger.info(f"跳过未启用的任务: {config.name}")
                continue

            try:
                # 创建调度条目
                entry = RedBeatSchedulerEntry(
                    name=config.name,
                    task=config.task,
                    schedule=config.cron,
                    args=config.args,
                    kwargs=config.kwargs,
                    app=celery_app,
                )

                # 检查是否已存在该任务
                if not overwrite:
                    try:
                        RedBeatSchedulerEntry.from_key(
                            f"{celery_app.conf.redbeat_key_prefix}:{config.name}", app=celery_app
                        )
                        logger.warning(f"任务 {config.name} 已存在，跳过加载")
                        continue
                    except KeyError:
                        pass

                # 保存到 Redis
                entry.save()
                logger.info(f"任务 {config.name} 已注册: {config.task}, 调度规则: {config.cron}")
                loaded_tasks.append(config.name)

            except Exception as e:
                logger.error(f"加载任务 {config.name} 失败: {e}")
                continue

        return loaded_tasks
