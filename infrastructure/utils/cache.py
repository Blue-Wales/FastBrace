#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : cache.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

import functools
import os
from contextlib import contextmanager

import redis
from loguru import logger

from infrastructure.core.settings import RedisDB, app_settings

redis_db = None

# Redis 连接超时配置（秒）
# socket_connect_timeout: 建立 TCP 连接的最长等待时间
# socket_timeout:         已建立连接上发送/接收指令的最长等待时间
_SOCKET_CONNECT_TIMEOUT = float(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "1"))
_SOCKET_TIMEOUT = float(os.getenv("REDIS_SOCKET_TIMEOUT", "2"))
_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))


def init_cache(redis_config: RedisDB):
    global redis_db
    redis_db = redis.ConnectionPool(
        host=redis_config.host,
        password=redis_config.password or None,
        port=redis_config.port,
        socket_connect_timeout=_SOCKET_CONNECT_TIMEOUT,
        socket_timeout=_SOCKET_TIMEOUT,
        max_connections=_MAX_CONNECTIONS,
        health_check_interval=30,
    )
    logger.info(
        f"Redis 连接池初始化完成：{redis_config.host}:{redis_config.port}，"
        f"连接超时={_SOCKET_CONNECT_TIMEOUT}s，读写超时={_SOCKET_TIMEOUT}s，"
        f"最大连接数={_MAX_CONNECTIONS}，密码={'已配置' if redis_config.password else '未配置'}"
    )
    return redis_db


@contextmanager
def get_redis_connection(db_pool):
    client = redis.Redis(connection_pool=db_pool)
    try:
        yield client
    finally:
        # 将连接归还到连接池，而不是关闭底层 socket
        client.close()


def access_token_cache(func):
    @functools.wraps(func)
    def wrapper(corp_id, corp_secret):
        with get_redis_connection(redis_db) as r:
            result = r.get(f"{corp_id}-{corp_secret}")
            if not result:
                result = func(corp_id, corp_secret)
                r.set(f"{corp_id}-{corp_secret}", result, ex=6000)
            return result

    return wrapper


def easy_sign_cache(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        redis_db = init_cache(app_settings.redis_db)
        with get_redis_connection(redis_db) as r:
            pub_key, pri_key = r.mget("easy_pub_key", "easy_pri_key")
            if not pub_key or not pri_key:
                pub_key, pri_key = await func(*args, **kwargs)
                r.set("easy_pub_key", pub_key, ex=60 * 60 * 24)
                r.set("easy_pri_key", pri_key, ex=60 * 60 * 24)
            return pub_key, pri_key

    return wrapper
