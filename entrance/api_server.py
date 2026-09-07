"""
@Project : FastBrace
@File    : api_server.py
@Author  : bright
@Date    : 2026-08-22
"""

import traceback

import click
import uvicorn
from loguru import logger

from infrastructure.core.app import create_app
from infrastructure.core.settings import app_settings
from infrastructure.events.event_bus_service import EventBusService


def _start_local_event_bus():
    """启动本地事件总线"""
    click.echo("启动本地事件总线")
    try:
        EventBusService.get_instance().start_local()
    except Exception as e:
        logger.error(f"本地事件总线启动失败: {e}, traceback: {traceback.format_exc()}")
        click.echo(f"本地事件总线启动失败 {e}", err=True)
        exit(1)


def _app_maker():
    """创建FastAPI应用"""
    app = create_app(app_settings)
    _start_local_event_bus()
    return app


def start_api_server(
    host: str, port: int, reload: bool, log_level: str, workers: int, access_log: bool
):
    """启动API服务"""
    uvicorn.run(
        "entrance.api_server:_app_maker",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        workers=workers,
        access_log=access_log,
        factory=True,
    )
