#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : permission_app.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 权限应用服务
"""

from api.response_body.json_response import ResponseModel
from api.response_body.permission_response import (
    DetailedPermissionNodeResponse,
    PermissionLevelInfo,
    PermissionSystemInfoResponse,
    PermissionTreeNodeResponse,
    SavePermissionResponse,
    ValidatePermissionResponse,
)
from application.base import BaseApplicationService
from domain.repo.interfaces.permission_resource import IPermissionResourceRepository
from domain.service.interfaces.permission import IPermissionService
from infrastructure.core.container import application_factory
from infrastructure.core.enum_var import BeanScope
from infrastructure.utils.context import get_user_permissions


@application_factory.autowire("permission_app_service", scope=BeanScope.PROTOTYPE.value)
class PermissionApplicationService(BaseApplicationService):
    """权限应用服务"""

    async def get_permission_tree(self, permission_service: IPermissionService):
        """获取权限树"""
        tree = await permission_service.get_permission_tree_for_role_creation()

        response_data = [PermissionTreeNodeResponse.model_validate(node) for node in tree]

        data = await self.generate_list_response(response_data, PermissionTreeNodeResponse)

        return data.model_dump()

    async def get_role_permission_tree(self, role_id: int, permission_service: IPermissionService):
        """获取角色权限树"""
        tree = await permission_service.get_role_permission_tree(role_id)

        response_data = [PermissionTreeNodeResponse.model_validate(node) for node in tree]

        data = await self.generate_list_response(response_data, PermissionTreeNodeResponse)

        return data.model_dump()

    async def save_role_permissions(
        self,
        role_id: int,
        permissions: dict[str, list[int]],
        permission_service: IPermissionService,
    ):
        """保存角色权限"""
        success = await permission_service.save_role_permissions(role_id, permissions)

        response_data = SavePermissionResponse(
            success=success,
            message="保存角色权限成功" if success else "保存角色权限失败",
            role_id=role_id,
        )

        data = ResponseModel(
            code=200 if success else 500,
            message=response_data.message,
            data=response_data.model_dump(),
        )

        return data.model_dump()

    async def get_role_detailed_permissions(
        self, role_id: int, permission_service: IPermissionService
    ):
        """获取角色细粒度权限"""
        detailed_permissions = await permission_service.get_filtered_detailed_permissions_for_frontend(
            role_id
        )

        response_data = [
            DetailedPermissionNodeResponse.model_validate(node) for node in detailed_permissions
        ]

        data = await self.generate_list_response(response_data, DetailedPermissionNodeResponse)

        return data.model_dump()

    async def get_user_detailed_permissions(self, permission_service: IPermissionService):
        """获取当前用户细粒度权限"""
        user_permissions = get_user_permissions()

        detailed_permissions = await permission_service.get_user_filtered_detailed_permissions(
            user_permissions
        )

        response_data = [
            DetailedPermissionNodeResponse.model_validate(node) for node in detailed_permissions
        ]

        data = await self.generate_list_response(response_data, DetailedPermissionNodeResponse)

        return data.model_dump()

    async def validate_permission(
        self,
        user_permissions: dict[str, list[int]],
        module_code: str,
        required_level: int,
        permission_service: IPermissionService,
    ):
        """验证权限"""
        has_permission = await permission_service.validate_user_permission(
            user_permissions, module_code, required_level
        )

        user_level = await permission_service.get_max_permission_level(
            user_permissions, module_code
        )

        response_data = ValidatePermissionResponse(
            has_permission=has_permission,
            module_code=module_code,
            required_level=required_level,
            user_level=user_level,
        )

        data = await self.generate_response(response_data, ValidatePermissionResponse)

        return data.model_dump()

    async def get_permission_system_info(self, permission_repo: IPermissionResourceRepository):
        """获取权限系统信息"""
        modules = await permission_repo.get_modules_only()
        actions = await permission_repo.get_actions_only()

        permission_levels = [
            PermissionLevelInfo(
                level=1, name="查看", description="可以查看模块对应页面以及页面中的数据"
            ),
            PermissionLevelInfo(
                level=2,
                name="操作",
                description="可以访问页面中的所有编辑/删除等涉及修改资源的操作",
            ),
            PermissionLevelInfo(level=3, name="导出", description="可以导出模块中的所有数据"),
        ]

        response_data = PermissionSystemInfoResponse(
            permission_levels=permission_levels,
            module_count=len(modules),
            action_count=len(actions),
        )

        data = await self.generate_response(response_data, PermissionSystemInfoResponse)

        return data.model_dump()
