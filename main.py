#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""框架命令行入口。

用于管理 API 服务、事件总线和定时任务进程。
"""

import os
import traceback

import click
from fastapi import applications
from loguru import logger

from entrance.api_server import start_api_server
from entrance.cron_job import start_cron_job
from entrance.event_bus import start_event_bus
from infrastructure.core.settings import app_settings
from infrastructure.utils.cache import init_cache
from infrastructure.utils.swagger_ui_patch import swagger_monkey_patch

# 应用Swagger UI补丁
applications.get_swagger_ui_html = swagger_monkey_patch


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="显示版本信息")
@click.pass_context
def cli(ctx, version):
    """
    FastBrace 命令行工具

    管理 API 服务、事件总线和定时任务。
    """
    if version:
        click.echo("FastBrace v1.0.0")
        return

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.group()
def server():
    """服务管理命令"""
    pass


@server.command()
@click.option(
    "--host",
    default="0.0.0.0",
    help="监听地址",
    show_default=True,
)
@click.option(
    "--port",
    default=8000,
    type=int,
    help="监听端口",
    show_default=True,
)
@click.option(
    "--debug/--no-debug",
    default=False,
    help="启用调试模式",
    show_default=True,
)
@click.option(
    "--reload/--no-reload",
    default=False,
    help="启用代码变更自动重载",
    show_default=True,
)
@click.option("--workers", default=1, type=int, help="工作进程数", show_default=True)
@click.option(
    "--log-level",
    default="info",
    type=click.Choice(["critical", "error", "warning", "info", "debug", "trace"]),
    help="日志级别",
    show_default=True,
)
@click.option(
    "--access-log/--no-access-log",
    default=True,
    help="启用访问日志",
    show_default=True,
)
def api(
    host: str,
    port: int,
    debug: bool,
    reload: bool,
    workers: int,
    log_level: str,
    access_log: bool,
):
    """启动 API 服务"""
    try:
        if debug:
            os.environ["LOG_DEBUG"] = "true"

        workers = 1 if reload else workers

        click.echo("正在启动 API 服务...")
        click.echo(f"服务地址: http://{host}:{port}")
        click.echo(f"调试模式: {'开启' if debug else '关闭'}")
        click.echo(f"自动重载: {'开启' if reload else '关闭'} (启用后工作进程固定为 1)")
        click.echo(f"工作进程: {workers}")
        click.echo(f"日志级别: {log_level.upper()}")
        click.echo(f"访问日志: {'开启' if access_log else '关闭'}")

        if debug:
            if not reload:
                reload = True
                click.echo("调试模式已自动启用代码重载")
            if log_level != "debug":
                log_level = "debug"
                click.echo("调试模式已自动将日志级别设为 debug")

        start_api_server(host, port, reload, log_level, workers, access_log)
    except KeyboardInterrupt:
        click.echo("\n服务已停止")
    except Exception as e:
        logger.error(f"服务启动失败: {e}, traceback: {traceback.format_exc()}")
        click.echo(f"\n服务启动失败: {e}", err=True)
        exit(1)


@server.command()
@click.option("--debug", is_flag=True, help="启用调试模式")
def events(debug: bool):
    """启动事件总线"""
    try:
        if debug:
            os.environ["LOG_DEBUG"] = "true"

        click.echo("正在启动事件总线...")
        init_cache(app_settings.redis_db)
        start_event_bus()
    except Exception as e:
        error_msg = f"命令执行失败: {e}"
        logger.error(f"{error_msg}, traceback: {traceback.format_exc()}")
        click.echo(error_msg, err=True)
        exit(1)


@server.command(name="cron_jobs")
@click.option("--debug", is_flag=True, help="启用调试模式")
def cron_jobs(debug: bool):
    """启动定时任务"""
    try:
        if debug:
            os.environ["LOG_DEBUG"] = "true"
        click.echo("正在启动定时任务...")
        start_cron_job()
    except Exception as e:
        error_msg = f"命令执行失败: {e}"
        logger.error(f"{error_msg}, traceback: {traceback.format_exc()}")
        click.echo(error_msg, err=True)
        exit(1)


@cli.group()
def db():
    """数据库管理命令"""
    pass


@db.command()
def migrate():
    """执行数据库迁移"""
    logger.info("正在执行数据库迁移...")
    # TODO: 接入 Alembic 迁移执行逻辑
    click.echo("数据库迁移命令暂未实现")


@db.command()
def seed():
    """初始化测试数据"""
    logger.info("正在初始化测试数据...")
    # TODO: 接入测试数据初始化逻辑
    click.echo("测试数据初始化命令暂未实现")


if __name__ == "__main__":
    cli()
