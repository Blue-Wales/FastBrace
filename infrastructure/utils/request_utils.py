#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : request_utils.py
@Author  : bright
@Date    : 2026-08-22
"""

from fastapi import Request


def get_client_ip(request: Request) -> str:
    """获取客户端真实IP地址

    优先级：
    1. X-Forwarded-For (负载均衡器/代理服务器)
    2. X-Real-IP (Nginx代理)
    3. X-Original-Forwarded-For (某些CDN)
    4. request.client.host (直连)

    :param request: FastAPI Request对象
    :return: 客户端IP地址
    """
    # 1. 检查 X-Forwarded-For 头部（最常用）
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For 可能包含多个IP，格式: "client, proxy1, proxy2"
        # 取第一个IP作为真实客户端IP
        return forwarded_for.split(",")[0].strip()

    # 2. 检查 X-Real-IP 头部（Nginx常用）
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # 3. 检查其他可能的头部
    original_forwarded = request.headers.get("X-Original-Forwarded-For")
    if original_forwarded:
        return original_forwarded.split(",")[0].strip()

    # 4. 直连情况，从client获取
    if request.client:
        return request.client.host

    # 5. 默认返回未知
    return "unknown"


def get_client_info(request: Request) -> dict:
    """获取完整的客户端信息

    :param request: FastAPI Request对象
    :return: 包含IP、User-Agent、端口等信息的字典
    """
    return {
        "ip": get_client_ip(request),
        "port": request.client.port if request.client else None,
        "user_agent": request.headers.get("User-Agent", ""),
        "host": request.headers.get("Host", ""),
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "headers": {
            "x-forwarded-for": request.headers.get("X-Forwarded-For"),
            "x-real-ip": request.headers.get("X-Real-IP"),
            "x-forwarded-proto": request.headers.get("X-Forwarded-Proto"),
            "referer": request.headers.get("Referer"),
        },
    }


def is_internal_ip(ip: str) -> bool:
    """判断是否为内网IP

    :param ip: IP地址
    :return: True表示内网IP
    """
    if ip == "unknown":
        return False

    # 内网IP范围
    internal_ranges = [
        "127.",  # 127.0.0.0/8  - 本地回环
        "10.",  # 10.0.0.0/8   - A类私有地址
        "192.168.",  # 192.168.0.0/16 - C类私有地址
        "172.16.",  # 172.16.0.0/12 - B类私有地址开始
        "172.17.",
        "172.18.",
        "172.19.",
        "172.20.",
        "172.21.",
        "172.22.",
        "172.23.",
        "172.24.",
        "172.25.",
        "172.26.",
        "172.27.",
        "172.28.",
        "172.29.",
        "172.30.",
        "172.31.",  # B类私有地址结束
        "169.254.",  # 169.254.0.0/16 - 链路本地地址
        "::1",  # IPv6 本地回环
        "fc00:",  # IPv6 唯一本地地址
        "fe80:",  # IPv6 链路本地地址
    ]

    return any(ip.startswith(prefix) for prefix in internal_ranges)


def get_real_client_ip(request: Request, trusted_proxies: list | None = None) -> str:
    """获取真实客户端IP（高级版本，支持可信代理配置）

    :param request: FastAPI Request对象
    :param trusted_proxies: 可信代理服务器IP列表
    :return: 真实的客户端IP地址
    """
    if trusted_proxies is None:
        trusted_proxies = ["127.0.0.1", "localhost", "::1"]

    # 获取直连IP
    direct_ip = request.client.host if request.client else "unknown"

    # 如果直连IP不在可信代理列表中，直接返回
    if direct_ip not in trusted_proxies:
        return direct_ip

    # 如果是可信代理，则查看代理头部
    return get_client_ip(request)
