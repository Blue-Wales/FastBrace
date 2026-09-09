#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : role_app.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 角色应用服务
"""

from api.request_body.role_request import CreateRole, UpdateRole
from api.response_body.role_response import RoleInfoResponse, RoleTreeResponse
from api.response_body.user_response import UserItemResponse
from application.base import BaseApplicationService
from domain.entity.role import RoleEntity
from domain.repo.role_repo import RoleRepository
from domain.repo.user_repo import UserRepository
from domain.service.role_service import RoleService
from domain.service.user_service import UserService
from infrastructure.core.container import application_factory
from infrastructure.core.enum_var import BeanScope
from infrastructure.utils.context import get_current_role_id


@application_factory.autowire("role_app_service", scope=BeanScope.PROTOTYPE.value)
class RoleApplicationService(BaseApplicationService):
    """角色应用服务"""

    async def create_role(self, role_data: CreateRole, role_repo: RoleRepository):
        """创建角色"""
        parent_role_id = role_data.parent_root_id

        role_entity = RoleEntity(**role_data.model_dump())

        result = await role_repo.add(parent_role_id, role_entity)

        data = await self.generate_response(result)

        return data.model_dump()


    async def update_role(self, role_data: UpdateRole, role_repo: RoleRepository):
        """更新角色"""
        role_entity = RoleEntity(**role_data.model_dump())
        role_entity.permission_check()

        result = await role_repo.save(role_entity)

        data = await self.generate_response(result)

        return data.model_dump()


    async def get_role_tree(self, role_id: int, role_repo: RoleRepository):
        """获取角色树"""
        role_tree = await role_repo.get_tree(role_id)
        data = await self.generate_response(role_tree, RoleTreeResponse)
        return data.model_dump()


    async def get_role_user_list(
        self,
        role_repo: RoleRepository,
        user_repo: UserRepository,
        role_domain_service: RoleService,
        user_domain_service: UserService,
        role_id: int,
        name: str | None = None,
        mobile: str | None = None,
        unregistered: bool = False,
        page: int | None = None,
        page_size: int | None = None,
    ):
        """获取角色相关用户列表"""
        role_info_dict = await role_domain_service.get_role_info(role_repo)
        relation_user_id_list = await role_domain_service.get_relation_users(role_repo, [role_id])
        if len(relation_user_id_list) == 0 and not unregistered:
            users, total = [], 0
        else:
            users, total = await user_domain_service.get_users(
                user_repo=user_repo,
                name=name,
                mobile=mobile,
                user_id_list=relation_user_id_list,
                role_info=role_info_dict,
                excluded=unregistered,
                page=page,
                page_size=page_size,
            )
        data = await self.generate_page_response(
            page=page, page_size=page_size, total=total, items=users, item_class=UserItemResponse
        )
        return data.model_dump()


    async def get_role(self, role_repo: RoleRepository, role_id: int):
        """获取角色"""
        role_entity = await role_repo.get_by_id(role_id)

        data = await self.generate_response(role_entity, RoleInfoResponse)

        return data.model_dump()


    async def delete_role(self, role_repo: RoleRepository, role_id: int):
        """删除角色"""
        role_entity = await role_repo.get_by_id(role_id)

        role_entity.delete_check()

        result = await role_repo.remove(role_entity.entity_id)

        data = await self.generate_response(result)

        return data.model_dump()


    async def add_users_to_role(self, role_repo: RoleRepository, role_id: int, user_ids: list[int]):
        """添加用户到角色"""
        result = await role_repo.add_users(role_id, user_ids)

        data = await self.generate_response(result)

        return data.model_dump()


    async def remove_users_from_role(
        self, role_repo: RoleRepository, role_id: int, user_ids: list[int]
    ):
        """从角色中移除用户"""
        result = await role_repo.remove_users(role_id, user_ids)

        data = await self.generate_response(result)

        return data.model_dump()


    async def get_current_role(self, role_repo: RoleRepository):
        """获取当前用户角色"""
        role_info = await role_repo.get_by_id(get_current_role_id())

        return {
            "role_id": str(role_info.entity_id),
            "role_name": role_info.name,
            "permissions": role_info.permissions,
            "code": 200,
        }
