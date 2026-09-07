#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : role_service.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 角色领域服务
"""

from domain.repo.role_repo import RoleRepository
from domain.service.base import BaseService
from infrastructure.core.container import domain_service_factory
from infrastructure.core.enum_var import BeanScope


@domain_service_factory.autowire("role_domain_service", scope=BeanScope.PROTOTYPE.value)
class RoleService(BaseService):
    """角色关联数据的领域服务实现。"""

    async def get_relation_users(self, role_repo: RoleRepository, role_ids: list[int]):
        """逐角色聚合并去重关联用户 ID。"""
        if len(role_ids) == 0:
            return []
        users_id_list = []
        for role_id in role_ids:
            role_entity = await role_repo.get_by_id(role_id=role_id)
            if role_entity is None:
                continue
            users_id_list.extend(role_entity.related_users)
        return list(set(users_id_list))

    async def get_role_info(self, role_repo: RoleRepository):
        """直接复用仓储的角色实体映射。"""
        return await role_repo.all_role_map()

    async def get_child_users_id(self, role_repo: RoleRepository, role_id: int):
        """复用闭包表查询后代角色关联用户。"""
        return await role_repo.child_role_user_id_list(role_id=role_id)

    async def fill_user_role_names(self, user_id: int, role_repo: RoleRepository):
        """将用户角色关联行转换为角色名称列表。"""
        role_map = await role_repo.all_role_map()
        user_role_relations = await role_repo.get_user_role_names(user_id)
        role_names = []
        for role_relation in user_role_relations:
            role_id = role_relation.role_id
            if role_id in role_map:
                role_names.append(role_map[role_id].name)
        return role_names
