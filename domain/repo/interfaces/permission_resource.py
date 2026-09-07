#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : permission_resource.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 权限资源仓储接口
"""

from typing import Protocol

from domain.entity.permission_resource import (
    DetailedPermissionNode,
    PermissionResourceEntity,
    PermissionTreeNode,
)


class IPermissionResourceRepository(Protocol):
    """权限资源查询、树构建和权限转换契约。

    权限资源由模块节点和动作节点组成。仓储负责把持久化的资源结构转换为
    领域实体和前端可消费的树，不负责当前用户的授权判断。
    """

    async def get_all_resources(self) -> list[PermissionResourceEntity]:
        """返回所有权限资源，供树构建和完整性校验使用。"""
        ...

    async def get_modules_only(self) -> list[PermissionResourceEntity]:
        """返回资源类型为模块的全部权限资源。"""
        ...

    async def get_actions_only(self) -> list[PermissionResourceEntity]:
        """返回资源类型为动作的全部权限资源。"""
        ...

    async def get_by_type_and_parent(
        self, resource_type: str, parent_id: int | None = None
    ) -> list[PermissionResourceEntity]:
        """按资源类型和可选父节点查询权限资源。

        Args:
            resource_type: 权限资源类型，如模块或动作。
            parent_id: 父资源实体 ID；`None` 表示只按类型筛选。

        Returns:
            匹配的权限资源实体列表。
        """
        ...

    async def build_module_tree(self) -> list[PermissionTreeNode]:
        """构建用于角色配权的模块权限树。

        Returns:
            按层级组织的根权限节点列表，每个节点包含可用权限级别。

        Notes:
            方法不设置任何角色的选中状态。
        """
        ...

    async def convert_coarse_to_detailed_permissions(
        self,
        coarse_permissions: dict[str, list[int]],
        filter_by_permission: bool = False,
    ) -> list[DetailedPermissionNode]:
        """将模块级权限映射转换为细粒度资源树。

        Args:
            coarse_permissions: 以模块 code 为键、权限级别列表为值的权限映射。
            filter_by_permission: 为 `True` 时只保留已授权节点及它们的必要父节点。

        Returns:
            包含模块和动作授权状态的细粒度权限树。
        """
        ...

    async def get_actions_by_module_and_level(
        self, module_code: str, level: int
    ) -> list[PermissionResourceEntity]:
        """查询模块在指定权限级别下可用的动作资源。

        Args:
            module_code: 模块权限 code。
            level: 粗粒度权限级别。

        Returns:
            属于该模块且覆盖该级别的动作资源列表。
        """
        ...

    async def validate_module_permissions(self, permissions: dict[str, list[int]]) -> bool:
        """校验模块 code 和权限级别是否均在当前资源定义中有效。

        Args:
            permissions: 待校验的模块权限映射。

        Returns:
            所有模块和级别均有效时返回 `True`。
        """
        ...
