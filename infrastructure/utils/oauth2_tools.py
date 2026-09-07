#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : oauth2_tools.py
@Author  : bright
@Date    : 2026-08-22
"""

import time

import jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from redis.exceptions import RedisError

from infrastructure.core.error_handler import AuthorizationError
from infrastructure.core.settings import app_settings
from infrastructure.utils.cache import get_redis_connection
from infrastructure.utils.dependencies import get_client_ip_dependency

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_token(token: str, redis_client=None):
    """校验token是否合法

    :param token: JWT token
    :param redis_client: Redis客户端，用于检查黑名单
    :return: 解码后的payload
    """
    try:
        # 先解码token获取payload
        decode_payload = jwt.decode(
            token, app_settings.jwt.secret_key, algorithms=[app_settings.jwt.algorithm]
        )

        # 检查token是否在黑名单中
        if redis_client:
            token_blacklist_key = f"blacklist_token:{token}"
            if redis_client.exists(token_blacklist_key):
                raise AuthorizationError("Token已被撤销")

            # 检查用户token版本是否有效
            user_id = decode_payload.get("sub")
            token_version = decode_payload.get("token_version", 0)
            if user_id and not check_user_token_version(user_id, token_version, redis_client):
                raise AuthorizationError("Token版本已失效")

        return decode_payload
    except jwt.ExpiredSignatureError:
        raise AuthorizationError("Token已过期")
    except jwt.InvalidTokenError:
        raise AuthorizationError("Token不合法")


def _redis_endpoint(request: Request) -> str:
    redis_pool = getattr(request.app.state, "redis_db", None)
    connection_kwargs = getattr(redis_pool, "connection_kwargs", {}) or {}
    host = connection_kwargs.get("host", "unknown")
    port = connection_kwargs.get("port", "unknown")
    return f"{host}:{port}"


async def check_token(
    request: Request,
    token: str = Depends(oauth2_scheme),
    client_ip: str = Depends(get_client_ip_dependency),
):
    """检测token是否合法

    :param request: FastAPI请求对象
    :param token: JWT token
    :param client_ip: 客户端IP
    :return: token payload
    """
    try:
        if getattr(request.state, "is_authenticated", False):
            user_info = getattr(request.state, "user_info", None)
            if user_info:
                return user_info

        if hasattr(request.app.state, "redis_db"):
            started_at = time.perf_counter()
            try:
                with get_redis_connection(request.app.state.redis_db) as client:
                    payload = verify_token(token, client)
                elapsed_ms = (time.perf_counter() - started_at) * 1000
                if elapsed_ms > 300:
                    logger.warning(
                        f"{client_ip} - Redis token校验耗时较高：{elapsed_ms:.1f}ms，"
                        f"endpoint={_redis_endpoint(request)}"
                    )
                return payload
            except (RedisError, OSError, TimeoutError) as redis_err:
                elapsed_ms = (time.perf_counter() - started_at) * 1000
                logger.warning(
                    f"{client_ip} - Redis token校验异常，降级为仅校验JWT签名和过期时间："
                    f"{type(redis_err).__name__}: {redis_err}，"
                    f"elapsed={elapsed_ms:.1f}ms，endpoint={_redis_endpoint(request)}"
                )

        return verify_token(token)
    except AuthorizationError:
        logger.info(f"{client_ip} - Token校验失败")
        raise


def revoke_token(token: str, redis_client, expire_time: int | None = None):
    """撤销token（加入黑名单）

    :param token: 要撤销的JWT token
    :param redis_client: Redis客户端
    :param expire_time: 黑名单过期时间（秒），默认使用token的剩余有效期
    """
    try:
        # 解码token获取过期时间
        decode_payload = jwt.decode(
            token, app_settings.jwt.secret_key, algorithms=[app_settings.jwt.algorithm]
        )

        token_blacklist_key = f"blacklist_token:{token}"

        if expire_time is None:
            # 计算token剩余有效期
            current_time = int(time.time())
            token_exp = decode_payload.get("exp", current_time)
            expire_time = max(token_exp - current_time, 0)

        # 将token加入黑名单，设置过期时间
        # TODO exp、current_time、redis_client.set ex单位需要对齐
        started_at = time.perf_counter()
        redis_client.set(token_blacklist_key, "revoked", ex=expire_time)
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        if elapsed_ms > 300:
            logger.warning(f"撤销token写入Redis耗时较高：{elapsed_ms:.1f}ms")
        logger.debug(f"Token已加入黑名单: {token[:20]}...")
        return True

    except jwt.InvalidTokenError:
        logger.warning("尝试撤销无效的token")
        return False
    except Exception as e:
        logger.error(f"撤销token失败: {e}")
        return False


def revoke_user_tokens(user_id: str, redis_client):
    """撤销用户的所有token（通过用户版本号机制）

    :param user_id: 用户ID
    :param redis_client: Redis客户端
    """
    try:
        # 增加用户的token版本号
        user_token_version_key = f"user_token_version:{user_id}"
        redis_client.incr(user_token_version_key)
        # 设置版本号过期时间（应该大于token的最大有效期）
        redis_client.expire(user_token_version_key, app_settings.jwt.refresh_expire_time * 2)
        logger.info(f"用户 {user_id} 的所有token已失效")
    except Exception as e:
        logger.warning(f"撤销用户token失败: {e}")


def check_user_token_version(user_id: str, token_version: int, redis_client) -> bool:
    """检查用户token版本是否有效

    :param user_id: 用户ID
    :param token_version: token中的版本号
    :param redis_client: Redis客户端
    :return: 版本是否有效
    """
    try:
        user_token_version_key = f"user_token_version:{user_id}"
        current_version = redis_client.get(user_token_version_key)

        if current_version is None:
            # 如果没有版本记录，认为是有效的
            return True

        current_version = int(current_version.decode("utf-8"))
        return token_version >= current_version
    except Exception as e:
        logger.warning(f"检查用户token版本失败: {e}")
        return True  # 出错时默认认为有效
