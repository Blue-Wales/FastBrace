#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : permission.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 权限领域服务接口
"""

from typing import Protocol

from domain.entity.permission_resource import DetailedPermissionNode, PermissionTreeNode


class IPermissionService(Protocol):
    """角色配权、粗细粒度权限转换和用户权限运算契约。

    服务组合权限资源仓储和角色仓储，但不处理 HTTP 响应、登录上下文或
    当前请求的权限装饰器。
    """

    async def get_permission_tree_for_role_creation(self) -> list[PermissionTreeNode]:
        """返回未设置选中状态的完整模块权限树。"""
        ...

    async def get_role_permission_tree(self, role_id: int) -> list[PermissionTreeNode]:
        """返回标记了指定角色当前授权级别的模块权限树。

        Args:
            role_id: 角色实体 ID。

        Returns:
            带选中状态的权限树；角色不存在时返回空列表。
        """
        ...

    async def save_role_permissions(self, role_id: int, permissions: dict[str, list[int]]) -> bool:
        """校验并替换角色的模块权限映射。

        Args:
            role_id: 角色实体 ID。
            permissions: 以模块 code 为键、权限级别列表为值的完整授权映射。

        Returns:
            权限有效且角色保存成功时返回 `True`；无效、角色不存在或保存失败时返回 `False`。
        """
        ...

    async def get_detailed_permissions_for_frontend(
        self, role_id: int
    ) -> list[DetailedPermissionNode]:
        """将角色的模块权限转换为完整细粒度树。

        Args:
            role_id: 角色实体 ID。

        Returns:
            包含已授权和未授权节点的细粒度权限树；角色不存在时返回空列表。
        """
        ...

    async def get_filtered_detailed_permissions_for_frontend(
        self, role_id: int
    ) -> list[DetailedPermissionNode]:
        """将角色权限转换为只包含已授权节点的细粒度树。"""
        ...

    async def get_user_detailed_permissions(
        self, user_permissions: dict[str, list[int]]
    ) -> list[DetailedPermissionNode]:
        """将已汇总的用户模块权限转换为完整细粒度树。"""
        ...

    async def get_user_filtered_detailed_permissions(
        self, user_permissions: dict[str, list[int]]
    ) -> list[DetailedPermissionNode]:
        """将用户模块权限转换为只包含已授权节点的细粒度树。"""
        ...

    async def validate_user_permission(
        self,
        user_permissions: dict[str, list[int]],
        module_code: str,
        required_level: int,
    ) -> bool:
        """判断用户在指定模块是否拥有所需权限级别。

        Args:
            user_permissions: 用户模块权限映射。
            module_code: 待校验的模块 code。
            required_level: 必须精确包含的权限级别。

        Returns:
            模块存在且级别已授权时返回 `True`。
        """
        ...

    async def get_permission_summary(self, permissions: dict[str, list[int]]) -> dict[str, str]:
        """将每个模块的权限级别转换为可展示的中文摘要。"""
        ...

    async def merge_permissions(
        self, permissions_list: list[dict[str, list[int]]]
    ) -> dict[str, list[int]]:
        """按模块合并多个权限映射，对权限级别取并集。"""
        ...

    async def get_max_permission_level(
        self, permissions: dict[str, list[int]], module_code: str
    ) -> int:
        """返回用户在指定模块的最大权限级别。

        Returns:
            模块不存在或级别列表为空时返回 `0`。
        """
        ...
