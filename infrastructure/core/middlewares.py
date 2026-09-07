#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : middlewares.py
@Author  : bright
@Date    : 2026-08-22
"""

import time
import uuid
from typing import ClassVar

from fastapi import FastAPI, Request
from loguru import logger
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import JSONResponse, Response

from infrastructure.core.enum_var import ErrorCode
from infrastructure.core.error_handler import AuthorizationError
from infrastructure.utils.cache import get_redis_connection
from infrastructure.utils.context import set_user_context
from infrastructure.utils.oauth2_tools import verify_token
from infrastructure.utils.request_utils import get_client_ip


class RequestLogMiddleWare(BaseHTTPMiddleware):
    EXCLUDE_LOG_PREFIXES: ClassVar[set[str]] = {"/health"}

    async def dispatch(self, request, call_next):
        """
        异步处理 HTTP 请求，记录请求时间并注入请求ID到响应头。
        参数:
            request: Starlette 请求对象。
            call_next: 调用下一个中间件或路由的异步函数。
        返回:
            response: 处理后的 Starlette 响应对象。
        """
        # 记录请求开始时间
        start_time = time.time()
        # 生成唯一请求ID
        request_id = uuid.uuid4().hex
        # 获取客户端IP
        client_ip = get_client_ip(request)

        response = await call_next(request)

        # 将请求ID绑定到日志上下文中
        logger.bind(request_id=request_id)

        process_time = f"{(time.time() - start_time):.4f}s"
        # 计算并设置请求耗时到响应头
        response.headers["X-Request-Time"] = process_time
        # 将请求ID添加到响应头
        response.headers["X-Request-Id"] = request_id
        # 添加客户端IP到响应头（可选，用于调试）
        response.headers["X-Client-IP"] = client_ip
        if not any(request.url.path.startswith(prefix) for prefix in self.EXCLUDE_LOG_PREFIXES):
            # 记录请求日志，包含客户端IP
            logger.debug(
                f"{client_ip} - {request.method} {request.url} "
                f"{response.status_code} {process_time}"
            )

        return response


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """JWT认证中间件 - 解析token并将用户信息存储到上下文变量中"""

    # 不需要认证的路径
    EXCLUDE_PATHS: ClassVar[set[str]] = {
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/login",
        "/health",
        "/ping",
        "/security/public-key",
        "/refresh-token",
        "/payment/pay_notify",
        "/payment/purchase",
        "/payment/refund",
        "/payment/remittance_voucher",
    }

    # 不需要认证的路径前缀
    EXCLUDE_PATH_PREFIXES: ClassVar[set[str]] = {"/docs", "/redoc", "/static", "/et", "/health"}

    def __init__(
        self,
        app,
        exclude_paths: set[str] | None = None,
        exclude_prefixes: set[str] | None = None,
    ):
        super().__init__(app)
        if exclude_paths:
            self.EXCLUDE_PATHS.update(exclude_paths)
        if exclude_prefixes:
            self.EXCLUDE_PATH_PREFIXES.update(exclude_prefixes)

    def _should_exclude_path(self, path: str) -> bool:
        """检查路径是否应该排除认证"""
        # 检查完全匹配的排除路径
        if path in self.EXCLUDE_PATHS:
            return True

        # 检查前缀匹配的排除路径
        return any(path.startswith(prefix) for prefix in self.EXCLUDE_PATH_PREFIXES)

    async def dispatch(self, request: Request, call_next) -> Response:
        """中间件主要逻辑 - 包含完整的上下文生命周期管理"""
        # 初始化用户上下文
        set_user_context(request, None, False)

        # 检查排除路径
        if self._should_exclude_path(request.url.path):
            return await call_next(request)

        # 解析JWT token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # 没有提供token或格式错误，直接返回认证失败响应
            return JSONResponse(
                status_code=200,
                content={
                    "code": ErrorCode.authorization_error.value,
                    "error": "凭证失忆了，请重新证明您是您",
                    "error_message": "缺少有效的认证令牌",
                },
            )

        token = auth_header.split(" ")[1]
        try:
            # 获取Redis连接进行token验证
            # 若 Redis 不可达，降级为无 Redis 验证模式（仅校验 JWT 签名和过期时间）
            redis_client = None
            if hasattr(request.app.state, "redis_db"):
                try:
                    redis_started_at = time.perf_counter()
                    with get_redis_connection(request.app.state.redis_db) as client:
                        redis_client = client
                        user_info = verify_token(token, redis_client)
                    redis_elapsed_ms = (time.perf_counter() - redis_started_at) * 1000
                    if redis_elapsed_ms > 300:
                        logger.warning(
                            f"Redis token校验耗时较高：{redis_elapsed_ms:.1f}ms，"
                            f"path={request.url.path}"
                        )
                except (RedisError, OSError, TimeoutError) as redis_err:
                    redis_elapsed_ms = (time.perf_counter() - redis_started_at) * 1000
                    logger.warning(
                        f"Redis 连接异常，降级为无 Redis token 验证："
                        f"{type(redis_err).__name__}: {redis_err}，"
                        f"elapsed={redis_elapsed_ms:.1f}ms，path={request.url.path}"
                    )
                    user_info = verify_token(token)
            else:
                user_info = verify_token(token)

            if not user_info:
                # token验证失败，直接返回认证失败响应
                return JSONResponse(
                    status_code=200,
                    content={
                        "code": ErrorCode.authorization_error.value,
                        "error": "凭证失忆了，请重新证明您是您",
                        "error_message": "认证令牌验证失败",
                    },
                )

            # token验证成功，设置用户上下文
            set_user_context(request, user_info, True)
            logger.debug(f"用户 {user_info.get('user_name', 'Unknown')} 认证成功")

        except AuthorizationError as e:
            # AuthorizationError异常，直接返回认证失败响应
            logger.debug(f"认证失败: {e.message}")
            return JSONResponse(
                status_code=200,
                content={
                    "code": ErrorCode.authorization_error.value,
                    "error": "凭证失忆了，请重新证明您是您",
                    "error_message": str(e.message),
                },
            )
        except Exception as e:
            # 其他验证异常，也返回认证失败响应
            logger.debug(f"Token验证失败: {e}")
            return JSONResponse(
                status_code=200,
                content={
                    "code": ErrorCode.authorization_error.value,
                    "error": "凭证失忆了，请重新证明您是您",
                    "error_message": f"认证令牌验证失败: {e!s}",
                },
            )

        # 处理请求
        return await call_next(request)


def init_middlewares(app: FastAPI) -> None:
    # 1. HTTPS重定向
    # app.add_middleware(HTTPSRedirectMiddleware)

    # 2. GZip压缩
    app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

    # 3. JWT认证中间件
    app.add_middleware(JWTAuthMiddleware)

    # 4. 请求日志
    app.add_middleware(RequestLogMiddleWare)

    # 5. CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    pass
