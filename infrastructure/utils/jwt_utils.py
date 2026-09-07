#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : jwt_utils.py
@Author  : bright
@Date    : 2026-08-22
"""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from loguru import logger

from infrastructure.core.error_handler import AuthorizationError
from infrastructure.core.settings import app_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def _create_token(data: dict, expire_time: int, redis_client=None):
    """创建JWT token

    :param data: token数据
    :param expire_time: 过期时间（秒）
    :param redis_client: Redis客户端，用于获取用户token版本
    :return: JWT token
    """
    if not redis_client:
        logger.warning("Redis客户端未初始化，JWT token部分功能无法使用")

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=expire_time)
    to_encode.update({"exp": expire})

    # 添加token版本号（用于批量撤销用户token）
    # 若 Redis 不可用，降级为 token_version=0，保证登录流程正常完成
    if redis_client and "sub" in data:
        user_id = data["sub"]
        user_token_version_key = f"user_token_version:{user_id}"
        try:
            token_version = redis_client.get(user_token_version_key)
            if token_version:
                to_encode["token_version"] = int(token_version.decode("utf-8"))
            else:
                to_encode["token_version"] = 0
        except Exception as err:
            logger.warning(f"Redis 获取用户token版本号失败，降级处理（token_version=0）: {err}")
            to_encode["token_version"] = 0

    return jwt.encode(to_encode, app_settings.jwt.secret_key, algorithm=app_settings.jwt.algorithm)


def create_access_token(data: dict, redis_client=None):
    """创建访问token

    :param data: token数据
    :param redis_client: Redis客户端
    :return: JWT token
    """
    return _create_token(data, app_settings.jwt.expire_time, redis_client)


def create_refresh_token(data: dict, redis_client=None):
    """
    创建刷新token
    :param data: token数据
    :param redis_client: Redis客户端
    :return: JWT token
    """
    return _create_token(data, app_settings.jwt.refresh_expire_time, redis_client)


async def check_token(token: str = Depends(oauth2_scheme)):
    """检测token是否合法

    :param token:
    :return:
    """
    try:
        return jwt.decode(
            token, app_settings.jwt.secret_key, algorithms=[app_settings.jwt.algorithm]
        )
    except jwt.ExpiredSignatureError:
        raise AuthorizationError("Token expired")
    except jwt.InvalidTokenError:
        raise AuthorizationError("Invalid token")
