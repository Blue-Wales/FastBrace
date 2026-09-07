#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : user_service.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 用户领域服务
"""

from domain.entity.role import RoleEntity
from domain.repo.interfaces.user import IUserRepository
from domain.service.base import BaseService
from infrastructure.core.container import domain_service_factory
from infrastructure.core.enum_var import BeanScope


@domain_service_factory.autowire("user_domain_service", scope=BeanScope.PROTOTYPE.value)
class UserService(BaseService):
    """用户查询与角色信息装配的领域服务实现。"""

    def __init__(
        self,
        user_repo: IUserRepository | None = None,
    ):
        super().__init__()
        self.user_repo = user_repo

    async def get_users(
        self,
        user_repo: IUserRepository,
        name: str | None = None,
        mobile: str | None = None,
        user_id_list: list[int] | None = None,
        role_info: dict[int, RoleEntity] | None = None,
        status: bool | None = None,
        excluded: bool = False,
        page: int | None = None,
        page_size: int | None = None,
    ):
        """组合用户查询结果与角色映射。"""
        users, total = await user_repo.list(
            name=name,
            mobile=mobile,
            user_id_list=user_id_list,
            status=status,
            page_size=page_size,
            page=page,
            excluded=excluded,
        )
        user_ids = [user.entity_id for user in users]
        user_role_map = await user_repo.user_role_relations(user_ids=user_ids)
        # 给用户实体添加角色信息
        [
            user_entity.add_roles_info(user_role_map.get(user_entity.entity_id, []), role_info)
            for user_entity in users
        ]
        return users, total
