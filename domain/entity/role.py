#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : role.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 角色领域实体
"""

from pydantic import Field

from domain.entity.base import Entity
from infrastructure.core.error_handler import DeleteError, PermissionDeniedError
from infrastructure.models.role import ADMIN_ROLE_CODE, ADMIN_ROLE_ID, ADMIN_ROLE_NAME


class RoleEntity(Entity):
    """
    角色实体
    """

    name: str = Field(title="角色名称")
    code: str = Field(title="角色唯一编码")
    permissions: dict[str, list[int]] = Field(title="权限配置信息", default_factory=dict)
    child_role: list["RoleEntity"] | None = Field(title="子角色", default_factory=list)
    related_users: list[int] | None = Field(title="关联用户", default_factory=list)

    class Config:
        from_attributes = True

    def permission_check(self):
        if (
            self.entity_id == ADMIN_ROLE_ID
            or self.name == ADMIN_ROLE_NAME
            or self.code == ADMIN_ROLE_CODE
        ):
            raise PermissionDeniedError(message="超级管理员角色无法删除")

    def delete_check(self):
        self.permission_check()
        if len(self.child_role) != 0 or len(self.related_users) != 0:
            raise DeleteError(message="角色下存在子角色或用户，无法删除")


RoleEntity.model_rebuild()
