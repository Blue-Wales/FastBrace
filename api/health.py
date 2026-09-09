#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : health.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 健康检查接口
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel
from sqlalchemy import text

from infrastructure.core.settings import app_settings
from infrastructure.utils.cache import get_redis_connection

health_router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应模型"""

    status: str
    version: str
    environment: str
    timestamp: str
    components: dict[str, Any]


class ComponentStatus(BaseModel):
    """单个组件状态"""

    status: str
    message: str = ""


async def check_database(request: Request) -> ComponentStatus:
    """检查数据库连通性"""
    try:
        engine = request.app.state.engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return ComponentStatus(status="healthy")
    except Exception as e:
        return ComponentStatus(status="unhealthy", message=str(e))


async def check_redis(request: Request) -> ComponentStatus:
    """检查 Redis 连通性"""
    try:
        with get_redis_connection(request.app.state.redis_db) as redis_client:
            redis_client.ping()
        return ComponentStatus(status="healthy")
    except Exception as e:
        return ComponentStatus(status="unhealthy", message=str(e))


@health_router.get("/health", response_model=HealthResponse, summary="健康检查")
async def health_check(request: Request) -> HealthResponse:
    """检查应用及其依赖组件的健康状态"""
    db_status = await check_database(request)
    redis_status = await check_redis(request)

    components = {
        "database": db_status.model_dump(),
        "redis": redis_status.model_dump(),
    }

    overall_status = "healthy"
    if any(c["status"] == "unhealthy" for c in components.values()):
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        version=app_settings.service_version,
        environment=app_settings.env,
        timestamp=datetime.utcnow().isoformat() + "Z",
        components=components,
    )


@health_router.get("/health/live", summary="存活探针")
async def liveness_probe():
    """Kubernetes 存活探针"""
    return {"status": "alive"}


@health_router.get("/health/ready", summary="就绪探针")
async def readiness_probe(request: Request):
    """Kubernetes 就绪探针"""
    try:
        # 检查关键依赖
        db_status = await check_database(request)
        redis_status = await check_redis(request)

        if db_status.status == "healthy" and redis_status.status == "healthy":
            return {"status": "ready"}
        return {"status": "not_ready", "reason": "依赖组件异常"}
    except Exception as e:
        return {"status": "not_ready", "reason": str(e)}
