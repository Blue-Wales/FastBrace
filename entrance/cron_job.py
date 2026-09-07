#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : cron_job.py
@Author  : bright
@Date    : 2026-08-22
"""

import traceback

import click
from loguru import logger

from infrastructure.core.app import auto_load_modules
from infrastructure.core.log import ModulesForLogger, init_logger
from infrastructure.cron.celery_beat import create_celery_beat


def _start_celery_beat() -> None:
    """
    启动定时任务
    :return:
    """
    try:
        # 初始化 Celery 应用
        click.echo("正在启动 Celery Beat 定时任务调度器...")
        create_celery_beat()
    except Exception as e:
        logger.error(f"Celery Beat 启动失败: {e}")
        logger.error(traceback.format_exc())
        click.echo(f"Celery Beat 启动失败: {e}", err=True)
        exit(1)


def start_cron_job():
    """启动定时任务"""
    init_logger(ModulesForLogger.CRON_JOB)

    # 预加载modules
    auto_load_modules(
        base_packages=[
            "application.file_app",
            "application.role_app",
            "application.user_app",
            "domain.events.user_events",
            "domain.repo.file_repo",
            "domain.repo.permission_resource_repo",
            "domain.repo.role_repo",
            "domain.repo.user_repo",
            "domain.service.email_service",
            "domain.service.permission_service",
            "domain.service.role_service",
            "domain.service.user_service",
            "infrastructure.models.file",
            "infrastructure.models.permission_resources",
            "infrastructure.models.role",
            "infrastructure.models.user",
            "infrastructure.events",
            "event_handlers.email_send_handler",
        ]
    )
    _start_celery_beat()
