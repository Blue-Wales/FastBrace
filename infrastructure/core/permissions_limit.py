#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : permissions_limit.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

import typing as t

from fastapi import Request
from loguru import logger

from infrastructure.core.enum_var import PermissionLevel, Permissions
from infrastructure.core.error_handler import PermissionDeniedError
from infrastructure.models.role import ADMIN_ROLE_ID
from infrastructure.utils.context import (
    get_current_user,
    get_user_permissions,
    is_authenticated,
)
from infrastructure.utils.permission_checker import PermissionChecker


def require_permission(
    permission_module: Permissions | None = None,
    required_permissions: list[PermissionLevel] | None = None,
) -> t.Callable:
    """
    依赖注入函数：检查功能权限

    :param permission_module: 权限模块名称
    :param required_permissions: 需要的权限操作列表
    :return: 用户信息字典
    :raises: HTTPException: 如果权限不足
    """
    def _check_permission(request: Request) -> dict[str, t.Any]:
        # 获取用户信息
        user_info = get_current_user(request)
        if not user_info or not is_authenticated(request):
            raise PermissionDeniedError("系统认证配置错误，请联系管理员")

        logger.debug(f"user_info: {user_info}")

        # 检查功能权限
        if permission_module is not None and required_permissions is not None:
            permissions = user_info.get("permissions", {})
            logger.debug(
                f"current user permissions: {permissions}, "
                f"checking module: {permission_module.value}, "
                f"required permissions: {required_permissions}"
            )

            # 获取用户在该模块的权限列表
            user_module_permissions = permissions.get(permission_module.value, [])
            if not isinstance(user_module_permissions, list):
                user_module_permissions = []

            # 检查用户是否拥有所有required_permissions中的权限
            missing_permissions = []
            for required_perm in required_permissions:
                if required_perm.value not in user_module_permissions:
                    missing_permissions.append(required_perm.value)

            if missing_permissions:
                perm_names = [PermissionLevel.get_name(perm) for perm in missing_permissions]
                raise PermissionDeniedError(
                    f"{permission_module.value}模块权限不足，缺少{', '.join(perm_names)}权限"
                )

        return user_info

    return _check_permission


def require_role(*role_ids: int) -> t.Callable:
    """
    依赖注入函数：检查角色权限

    :param role_ids: 允许的角色ID列表
    :return: 用户信息字典
    :raises: HTTPException: 如果角色权限不足
    """
    def _check_role(request: Request) -> dict[str, t.Any]:
        # 获取用户信息
        user_info = get_current_user(request)
        if not user_info or not is_authenticated(request):
            raise PermissionDeniedError("系统认证配置错误，请联系管理员")

        # 检查角色权限
        current_role_id = user_info.get("role_id")
        if current_role_id not in role_ids:
            raise PermissionDeniedError("角色权限不足")

        return user_info

    return _check_role


def require_admin() -> t.Callable:
    """
    依赖注入函数：要求超级管理员权限

    :return: 用户信息字典
    :raises: HTTPException: 如果不是超级管理员
    """
    return require_role(ADMIN_ROLE_ID)


def require_permission_expression(permission_expression) -> t.Callable:
    """
    依赖注入函数：基于Permission表达式的权限检查

    :param permission_expression: Permission表达式对象
    :return: 用户信息字典
    :raises: HTTPException: 如果权限不足
    """
    def _check_permission_expression(request: Request) -> dict[str, t.Any]:
        # 检查用户认证
        user_info = get_current_user(request)
        if not user_info or not is_authenticated(request):
            raise PermissionDeniedError("系统认证配置错误，请联系管理员")

        logger.debug(f"用户信息: {user_info}")

        # 获取用户权限，格式化为Permission对象需要的格式
        formatted_permissions = get_user_permissions(request)
        logger.debug(f"格式化后的权限: {formatted_permissions}")
        logger.debug(f"检查权限表达式: {permission_expression}")

        if not PermissionChecker.check(permission_expression, formatted_permissions):
            required_modules = PermissionChecker.get_required_permissions(permission_expression)
            logger.warning(
                f"用户权限不足: 需要 {permission_expression}, 涉及模块: {required_modules}"
            )
            raise PermissionDeniedError(f"权限不足: 需要 {permission_expression}")

        logger.info(f"权限验证通过: {permission_expression}")
        return user_info

    return _check_permission_expression


# 组合权限检查函数
def require_permission_and_role(
    permission_module: Permissions | None = None,
    required_permissions: list[PermissionLevel] | None = None,
    role_ids: tuple[int, ...] | None = None,
) -> t.Callable:
    """
    依赖注入函数：同时检查功能权限和角色权限

    :param permission_module: 权限模块名称
    :param required_permissions: 需要的权限操作列表
    :param role_ids: 允许的角色ID列表
    :return: 用户信息字典
    :raises: HTTPException: 如果权限不足
    """
    def _check_permission_and_role(request: Request) -> dict[str, t.Any]:
        # 获取用户信息
        user_info = get_current_user(request)
        if not user_info or not is_authenticated(request):
            raise PermissionDeniedError("系统认证配置错误，请联系管理员")

        logger.debug(f"user_info: {user_info}")

        # 检查角色权限
        if role_ids is not None:
            current_role_id = user_info.get("role_id")
            if current_role_id not in role_ids:
                raise PermissionDeniedError("角色权限不足")

        # 检查功能权限
        if permission_module is not None and required_permissions is not None:
            permissions = user_info.get("permissions", {})
            logger.debug(
                f"current user permissions: {permissions}, "
                f"checking module: {permission_module.value}, "
                f"required permissions: {required_permissions}"
            )

            # 获取用户在该模块的权限列表
            user_module_permissions = permissions.get(permission_module.value, [])
            if not isinstance(user_module_permissions, list):
                user_module_permissions = []

            # 检查用户是否拥有所有required_permissions中的权限
            missing_permissions = []
            for required_perm in required_permissions:
                if required_perm.value not in user_module_permissions:
                    missing_permissions.append(required_perm.value)

            if missing_permissions:
                perm_names = [PermissionLevel.get_name(perm) for perm in missing_permissions]
                raise PermissionDeniedError(
                    f"{permission_module.value}模块权限不足，缺少{', '.join(perm_names)}权限"
                )

        return user_info

    return _check_permission_and_role
