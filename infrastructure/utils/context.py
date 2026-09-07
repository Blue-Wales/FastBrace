#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : context.py
@Author  : bright
@Date    : 2026-08-22
"""

from contextvars import ContextVar
from typing import Any

from fastapi import Depends, HTTPException, Request

_current_user_context_var: ContextVar[dict[str, Any] | None] = ContextVar(
    "current_user_context", default=None
)
_access_token_context_var: ContextVar[str | None] = ContextVar(
    "access_token_context", default=None
)


def load_current_user_context(request: Request) -> None:
    """将当前请求的用户信息与访问令牌写入上下文变量，供应用服务层读取。"""
    _current_user_context_var.set(getattr(request.state, "user_info", None))
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[7:] if auth_header.startswith("Bearer ") else None
    _access_token_context_var.set(token)


def get_current_token() -> str | None:
    """获取当前请求的访问令牌。"""
    return _access_token_context_var.get()


def set_user_context(
    request: Request,
    user_info: dict[str, Any] | None,
    is_authenticated: bool = False,
) -> None:
    """
    设置用户上下文到request.state

    :param request: FastAPI请求对象
    :param user_info: 用户信息字典
    :param is_authenticated: 是否已认证
    """
    request.state.user_info = user_info
    request.state.is_authenticated = is_authenticated


def get_current_user(request: Request | None = None) -> dict[str, Any] | None:
    """
    获取当前用户信息

    :param request: FastAPI请求对象，如果为None则尝试从当前请求获取
    :return: 用户信息字典，如果未认证则返回None
    """
    if request is None:
        return _current_user_context_var.get()

    return getattr(request.state, "user_info", None)


def get_current_user_id(request: Request | None = None) -> int | None:
    """
    获取当前用户ID

    :param request: FastAPI请求对象
    :return: 用户ID，如果未认证则返回None
    """
    user_info = get_current_user(request)
    if user_info:
        user_id = user_info.get("sub")
        return int(user_id) if user_id else None
    return None


def get_current_role_id(request: Request | None = None) -> int | None:
    """
    获取当前角色ID

    :param request: FastAPI请求对象
    :return: 角色ID，如果未认证则返回None
    """
    user_info = get_current_user(request)
    return user_info.get("role_id") if user_info else None


def is_authenticated(request: Request | None = None) -> bool:
    """
    检查用户是否已认证

    :param request: FastAPI请求对象
    :return: 是否已认证
    """
    if request is None:
        return False

    return getattr(request.state, "is_authenticated", False)


def get_user_permissions(request: Request | None = None) -> dict[str, list[int]]:
    """
    获取用户权限，格式化为Permission表达式需要的格式

    :param request: FastAPI请求对象
    :return: Dict[str, List[int]]: 权限字典，格式：{"模块名": [级别列表]}
    """
    user_info = get_current_user(request)
    if not user_info:
        return {}

    permissions = user_info.get("permissions", {})
    formatted_permissions = {}

    for module, perms in permissions.items():
        if isinstance(perms, list):
            formatted_permissions[module] = perms
        elif isinstance(perms, int):
            # 如果是单个整数，转换为列表
            formatted_permissions[module] = [perms]
        else:
            formatted_permissions[module] = []

    return formatted_permissions


def has_permission(request: Request | None, permission: str, level: int = 1) -> bool:
    """
    检查用户是否有指定权限

    :param request: FastAPI请求对象
    :param permission: 权限名称
    :param level: 权限级别 (1: 只读, 2: 读写)
    :return: 是否有权限
    """
    permissions = get_user_permissions(request)
    user_level = permissions.get(permission, [])
    return level in user_level


def get_username(request: Request | None = None) -> str | None:
    """
    获取用户名

    :param request: FastAPI请求对象
    :return: 用户名
    """
    user_info = get_current_user(request)
    return user_info.get("user_name") if user_info else None


def require_authentication(request: Request) -> dict[str, Any]:
    """
    要求用户必须已认证，否则抛出异常

    :param request: FastAPI请求对象
    :return: 用户信息
    :raises: HTTPException: 如果用户未认证
    """
    user_info = get_current_user(request)
    if not user_info or not is_authenticated(request):
        raise HTTPException(status_code=401, detail="需要登录")
    return user_info


def clear_user_context(request: Request) -> None:
    """
    清理用户上下文

    :param request: FastAPI请求对象
    """
    if hasattr(request.state, "user_info"):
        delattr(request.state, "user_info")
    if hasattr(request.state, "is_authenticated"):
        delattr(request.state, "is_authenticated")


def get_context_info(request: Request) -> dict[str, Any]:
    """
    获取当前上下文信息 - 用于调试

    :param request: FastAPI请求对象
    :return: 包含所有上下文信息的字典
    """
    return {
        "is_authenticated": is_authenticated(request),
        "user_info": get_current_user(request),
        "user_id": get_current_user_id(request),
        "role_id": get_current_role_id(request),
        "username": get_username(request),
        "permissions": get_user_permissions(request),
    }


def get_current_request() -> Request:
    """
    获取当前请求对象的依赖注入函数

    :return: 当前请求对象
    """
    def _get_current_request(request: Request) -> Request:
        return request

    return Depends(_get_current_request)


def get_current_user_dependency() -> dict[str, Any] | None:
    """
    获取当前用户的依赖注入函数

    :return: 当前用户信息
    """
    def _get_current_user(request: Request) -> dict[str, Any] | None:
        return get_current_user(request)

    return Depends(_get_current_user)


def get_current_user_id_dependency() -> int | None:
    """
    获取当前用户ID的依赖注入函数

    :return: 当前用户ID
    """
    def _get_current_user_id(request: Request) -> int | None:
        return get_current_user_id(request)

    return Depends(_get_current_user_id)


def get_current_role_id_dependency() -> int | None:
    """
    获取当前角色ID的依赖注入函数

    :return: 当前角色ID
    """
    def _get_current_role_id(request: Request) -> int | None:
        return get_current_role_id(request)

    return Depends(_get_current_role_id)


def get_user_permissions_dependency() -> dict[str, list[int]]:
    """
    获取用户权限的依赖注入函数

    :return: 用户权限字典
    """
    def _get_user_permissions(request: Request) -> dict[str, list[int]]:
        return get_user_permissions(request)

    return Depends(_get_user_permissions)


def require_authentication_dependency() -> dict[str, Any]:
    """
    要求用户认证的依赖注入函数

    :return: 用户信息
    :raises: HTTPException: 如果用户未认证
    """
    def _require_authentication(request: Request) -> dict[str, Any]:
        return require_authentication(request)

    return Depends(_require_authentication)


def is_authenticated_dependency() -> bool:
    """
    检查用户是否已认证的依赖注入函数

    :return: 是否已认证
    """
    def _is_authenticated(request: Request) -> bool:
        return is_authenticated(request)

    return Depends(_is_authenticated)
