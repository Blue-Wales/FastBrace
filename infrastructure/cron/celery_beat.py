#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : celery_beat.py
@Author  : bright
@Date    : 2026-08-22
"""

from celery import Celery

from infrastructure.core.log import logger_manager
from infrastructure.core.settings import app_settings
from infrastructure.cron.task_loader import TaskManager


def create_celery_beat() -> None:
    # 初始化 Celery 应用
    celery_app = Celery(
        "cron_job",
        broker=app_settings.celery.broker_url,
        backend=app_settings.celery.result_backend,
        redbeat_redis_url=app_settings.celery.broker_url,
    )

    # 更新 Celery 配置
    celery_app.conf.update(
        beat_schedule={},
        beat_scheduler=app_settings.celery.beat.scheduler,
        beat_schedule_file=None,
        beat_max_loop_interval=app_settings.celery.beat.beat_max_loop_interval,
        beat_sync_every=app_settings.celery.beat.beat_sync_every,
        task_serializer=app_settings.celery.task_serializer,
        accept_content=app_settings.celery.accept_content,
        result_serializer=app_settings.celery.result_serializer,
        enable_utc=app_settings.celery.enable_utc,
        timezone=app_settings.celery.timezone,
        result_expires=app_settings.celery.result_expires,
        redbeat_key_prefix=app_settings.celery.beat.key_prefix,
        module_path=app_settings.celery.beat.module_path,
    )
    TaskManager.register_tasks(celery_app)

    celery_app.Beat(loglevel=logger_manager.log_level).run()
