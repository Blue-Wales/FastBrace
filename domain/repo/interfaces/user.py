#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : user.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 用户仓储接口
"""

import builtins
from typing import Any, Protocol

from domain.entity.user import UserEntity
from domain.repo.interfaces.base import IBaseRepository
from domain.value_object.user_vo import UserInfoVO, UserMobileVO, UserSummaryVO


class IUserRepository(IBaseRepository, Protocol):
    """用户、用户角色关联和通知联系信息的持久化契约。

    该仓储使用用户实体 ID 作为领域标识，负责用户查询、状态、角色关联、
    和通知渠道所需的投影查询。密码哈希、权限决策和事务提交不属于本接口。
    """

    async def get_by_id(self, user_id: int | str, id_type="entity_id") -> UserEntity:
        """根据指定用户标识字段查询用户。

        Args:
            user_id: 待查询的标识值。
            id_type: 用户模型上的标识字段，默认为 `entity_id`。

        Returns:
            匹配的用户实体。

        Raises:
            NotFoundError: 用户不存在。
            AttributeError: `id_type` 不是合法用户模型字段。
        """
        ...

    async def get_by_username(self, username: str) -> UserEntity | None:
        """根据唯一用户名查询用户，未找到时返回 `None`。"""
        ...

    async def add(self, user_entity: UserEntity) -> None:
        """将新用户加入当前事务。

        Args:
            user_entity: 已生成实体 ID 且完成业务校验的用户实体。

        Notes:
            方法不执行 flush 或 commit。
        """
        ...

    async def delete(self, user_id: int) -> int:
        """根据用户实体 ID 删除用户并返回受影响行数。"""
        ...

    async def batch_add(self, user_entity_list: list[UserEntity]) -> bool:
        """批量新增或更新用户，并保留已存在用户的实体 ID。

        Args:
            user_entity_list: 待批量写入的用户实体列表。

        Returns:
            批量 upsert 执行完成时返回 `True`。
        """
        ...

    async def list(
        self,
        page: int | None = None,
        page_size: int | None = None,
        name: str | None = None,
        nick_name: str | None = None,
        mobile: str | None = None,
        user_id_list: list[int] | None = None,
        status: bool | None = None,
        excluded: bool = False,
    ) -> tuple[list[UserEntity], int]:
        """按条件筛选用户，并可选分页。

        Args:
            page: 从 `1` 开始的页码；与 `page_size` 同时传入时生效。
            page_size: 每页数量。
            name: 姓名模糊筛选值。
            nick_name: 昵称模糊筛选值。
            mobile: 手机号模糊筛选值。
            user_id_list: 用户实体 ID 列表。
            status: 可选的用户状态过滤值。
            excluded: 为 `True` 时排除 `user_id_list`，否则只保留该列表。

        Returns:
            `(用户实体列表, 总数)`；未分页时总数按当前实现返回 `0`。
        """
        ...

    async def user_role_relations(
        self, user_ids: builtins.list[int]
    ) -> dict[int, builtins.list[int]]:
        """批量查询用户与角色的关联映射。

        Args:
            user_ids: 用户实体 ID 列表。

        Returns:
            以用户 ID 为键、角色 ID 列表为值的映射。
        """
        ...

    async def has_role(self, user_id: int, role_id: int) -> bool:
        """判断用户是否直接关联指定角色。"""
        ...

    async def save(self, user_entity: UserEntity) -> int:
        """根据实体 ID 更新用户的非空持久化字段。

        Args:
            user_entity: 包含实体 ID 和待更新字段的用户实体。

        Returns:
            受影响的用户记录数。
        """
        ...

    async def update_related_roles(self, user_id: int, role_ids: builtins.list[int]) -> int:
        """用新角色列表完全替换用户的直接角色关联。

        Args:
            user_id: 用户实体 ID。
            role_ids: 替换后的角色实体 ID 列表；空列表表示清空关联。

        Returns:
            替换前被删除的关联记录数。
        """
        ...

    async def name_list(
        self, name: str | None = None, status: bool = True
    ) -> builtins.list[dict[str, Any]]:
        """查询用户名称选项。

        Args:
            name: 可选的姓名模糊筛选值。
            status: 需要匹配的用户状态。

        Returns:
            包含字符串 `user_id` 和 `name` 的选项列表。
        """
        ...

    async def change_status(
        self, user_id_list: builtins.list[int], status: bool, current_user_name: str
    ) -> int:
        """批量更新用户状态和最后操作人。

        Args:
            user_id_list: 待更新的用户实体 ID 列表。
            status: 目标状态。
            current_user_name: 记录到 `last_operator` 的操作人名称。

        Returns:
            受影响的用户记录数。
        """
        ...

    async def get_default_role_id(self, user_id: int) -> int:
        """返回用户直接关联的第一个角色 ID。

        Raises:
            PermissionError: 用户没有关联角色。
        """
        ...

    async def get_summary_info(self, entity_id: int) -> UserSummaryVO:
        """查询启用用户的 ID 和姓名摘要。

        Raises:
            NotFoundError: 用户不存在或已禁用。
        """
        ...

    async def get_user_mobile_by_id(self, entity_id: int) -> UserMobileVO:
        """查询启用用户的 ID、姓名和手机号。

        Raises:
            NotFoundError: 用户不存在或已禁用。
        """
        ...

    async def get_user_by_mobile(self, mobile: str) -> UserInfoVO | None:
        """根据手机号查询未禁用用户的对外信息。

        Returns:
            用户信息值对象；未找到时返回 `None`。
        """
        ...

    async def get_all_normal_users(self) -> builtins.list[dict[str, int]]:
        """返回所有未禁用用户的 `entity_id` 映射列表。"""
        ...
