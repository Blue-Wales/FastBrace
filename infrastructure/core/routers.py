#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : routers.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 路由配置
"""

from fastapi import FastAPI

from api.file import file_router
from api.health import health_router
from api.login import login_router
from api.permission import permission_router
from api.role import role_router
from api.security import security_router
from api.test import test_router
from api.user import user_router
from infrastructure.core.settings import AppSettings


def init_router(app: FastAPI, app_settings: AppSettings):
    """初始化并注册全部 API 路由。

    JWT 认证由中间件统一处理，不在单个路由中重复声明。
    """
    # 健康检查始终可用
    app.include_router(health_router, tags=["健康检查"])

    # 安全能力
    app.include_router(security_router, prefix="/security", tags=["安全"])

    # 文件管理
    app.include_router(file_router, prefix="/file", tags=["文件"])

    # 认证登录
    app.include_router(login_router, tags=["认证"])

    # 用户管理
    app.include_router(user_router, prefix="/users", tags=["用户"])

    # 角色管理
    app.include_router(role_router, prefix="/role", tags=["角色"])

    # 权限管理
    app.include_router(permission_router, prefix="/permissions", tags=["权限"])

    # 测试路由仅在非生产环境注册
    if app_settings.env != "prod":
        app.include_router(test_router, prefix="/token", tags=["测试"])
