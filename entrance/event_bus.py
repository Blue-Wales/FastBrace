"""
@Project : FastBrace
@File    : event_bus.py
@Author  : bright
@Date    : 2026-08-22
"""

import traceback

import click
from loguru import logger

from infrastructure.core.app import auto_load_modules
from infrastructure.core.log import ModulesForLogger, init_logger
from infrastructure.core.settings import app_settings
from infrastructure.events.event_bus_service import EventBusService
from infrastructure.utils.database import init_database


def _start_cross_event_bus():
    """启动跨域事件总线"""
    click.echo("启动跨域事件总线")
    try:
        EventBusService.get_instance().start_cross()
    except Exception as e:
        logger.error(f"跨域事件总线启动失败: {e}, traceback: {traceback.format_exc()}")
        click.echo(f"跨域事件总线启动失败 {e}", err=True)
        exit(1)


def start_event_bus():
    """启动事件总线"""
    init_logger(ModulesForLogger.EVENT_BUS)

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
    init_database(app_settings.db)
    _start_cross_event_bus()
