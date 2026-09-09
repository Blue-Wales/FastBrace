#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : dependencies.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

from fastapi import Depends, Request

from infrastructure.utils.request_utils import get_client_info, get_client_ip


def get_client_ip_dependency(request: Request) -> str:
    """依赖注入：获取客户端IP

    使用方式:
    @app.get("/api/test")
    async def test_endpoint(client_ip: str = Depends(get_client_ip_dependency)):
        return {"your_ip": client_ip}
    """
    return get_client_ip(request)


def get_client_info_dependency(request: Request) -> dict:
    """依赖注入：获取客户端完整信息

    使用方式:
    @app.get("/api/info")
    async def info_endpoint(client_info: dict = Depends(get_client_info_dependency)):
        return client_info
    """
    return get_client_info(request)


# 简化的别名
ClientIP = Depends(get_client_ip_dependency)
ClientInfo = Depends(get_client_info_dependency)
