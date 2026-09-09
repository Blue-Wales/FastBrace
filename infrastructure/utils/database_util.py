#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : database_util.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 数据库工具模块
"""

from infrastructure.core.settings import app_settings


def get_database_url(escape_percent=False):
    """从YAML配置文件中获取数据库URL"""
    # 构建数据库URL
    db_config = app_settings.db

    db_config.username = db_config.username.replace("@", "%40")

    db_config.password = db_config.password.replace("@", "%40")

    database_url = f"{db_config.drivername}://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}"

    # 处理特殊字符编码问题
    if "mysql" in db_config.drivername:
        database_url += "?charset=utf8mb4"

    if escape_percent:
        database_url = database_url.replace("%", "%%")
    return database_url
