#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : role.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 角色仓储接口
"""

from typing import Protocol

from domain.entity.role import RoleEntity


class IRoleRepository(Protocol):
    """角色、角色闭包树和用户角色关联的持久化契约。

    所有角色关系都使用角色实体 ID。仓储负责树关系和用户关联的数据访问，
    角色是否可创建、删除或授权由应用层判断。
    """

    async def add(self, parent_role_id: int, role_entity: RoleEntity) -> str:
        """创建角色并维护其与父角色的闭包表关系。

        Args:
            parent_role_id: 父角色实体 ID。
            role_entity: 已生成实体 ID 的新角色。

        Returns:
            新角色实体 ID 的字符串形式。

        Raises:
            DuplicateEntryError: 角色名称或 code 冲突。
        """
        ...

    async def get_tree(self, root_id: int = 1) -> RoleEntity | None:
        """查询以指定角色为根的完整角色树。

        Args:
            root_id: 根角色实体 ID。

        Returns:
            已填充 `child_role` 的根角色实体。

        Raises:
            NotFoundError: 根角色不存在。
        """
        ...

    async def save(self, role_entity: RoleEntity) -> int:
        """根据实体 ID 更新角色的可持久化字段。

        Args:
            role_entity: 包含最终字段值的角色实体；树和用户关联字段不会写入。

        Returns:
            受影响的角色记录数。
        """
        ...

    async def user_id_list(self, role_ids: list[int]) -> list[int]:
        """查询任一指定角色关联的去重用户 ID 列表。

        Args:
            role_ids: 角色实体 ID 列表。
        """
        ...

    async def get_by_id(self, role_id: int) -> RoleEntity:
        """查询角色详情、直接子角色和关联用户。

        Args:
            role_id: 角色实体 ID。

        Returns:
            已填充 `child_role` 和 `related_users` 的角色实体。

        Raises:
            NotFoundError: 目标角色不存在。
        """
        ...

    async def remove(self, role_id: int) -> bool:
        """删除角色与其作为后代的闭包表关系。

        Args:
            role_id: 待删除的角色实体 ID。

        Returns:
            角色记录和闭包关系均被删除时返回 `True`。
        """
        ...

    async def add_users(self, role_id: int, user_ids: list[int]) -> int:
        """批量建立角色与用户的关联。

        Args:
            role_id: 目标角色实体 ID。
            user_ids: 需要关联的用户实体 ID 列表。

        Returns:
            数据库报告的受影响行数。
        """
        ...

    async def remove_users(self, role_id: int, user_ids: list[int]) -> int:
        """批量删除角色与用户的关联。

        Args:
            role_id: 目标角色实体 ID。
            user_ids: 需要移除的用户实体 ID 列表。

        Returns:
            被删除的关联记录数。
        """
        ...

    async def all_role_map(self) -> dict[int, RoleEntity]:
        """返回以角色实体 ID 为键的全量角色映射。"""
        ...

    async def child_role_user_id_list(self, role_id: int, depth: int | None = None) -> list[int]:
        """查询子角色关联的去重用户 ID。

        Args:
            role_id: 起始角色实体 ID。
            depth: 可选的最大后代深度；不传时查询所有真正子角色。

        Returns:
            匹配子角色下的去重用户 ID 列表。
        """
        ...

    async def ancestor_role_user_id_list(self, role_ids: list[int]) -> list[int]:
        """查询指定角色的所有上级角色所关联的用户。

        Args:
            role_ids: 用于反向查找祖先节点的角色实体 ID 列表。

        Returns:
            所有祖先角色下的去重用户 ID 列表。
        """
        ...

    async def get_user_role_names(self, user_id: int) -> list:
        """查询用户关联的角色 ID 行。

        Args:
            user_id: 用户实体 ID。

        Returns:
            包含 `role_id` 字段的查询行列表。角色名称由调用方结合角色映射解析。
        """
        ...
