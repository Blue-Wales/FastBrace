#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : user.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 用户领域实体
"""

from datetime import datetime
from typing import Any

from pydantic import Field, computed_field, model_validator

from domain.entity.base import Entity
from domain.entity.role import RoleEntity
from infrastructure.core.error_handler import PermissionDeniedError
from infrastructure.utils.admin_constants import ADMIN_USER_ID, ADMIN_USERNAME
from infrastructure.utils.password_utils import hash_password


class UserEntity(Entity):
    name: str | None = Field(title="姓名", default=None)
    username: str | None = Field(title="用户名", default=None)
    password: str | None = Field(title="密码", default=None)
    password_hash: str | None = Field(title="密码hash", default=None)
    mobile: str | None = Field(title="手机号", default=None)
    gender: int | None = Field(title="性别(2：女，1：男, 0: 未定义)", default=None)
    email: str | None = Field(title="邮箱", default=None)
    personal_avatar: list[dict[str, Any]] | None = Field(title="头像", default_factory=list)
    thumb_avatar: list[dict[str, Any]] | None = Field(title="缩略头像", default_factory=list)
    personal_qr_code: list[dict[str, Any]] | None = Field(title="二维码", default_factory=list)
    status: bool | None = Field(title="状态（启用/停用）", default=None)
    nick_name: str | None = Field(title="昵称", default=None)
    update_time: datetime | None = Field(title="修改时间", default=None)
    create_time: datetime | None = Field(title="创建时间", default=None)
    roles: list[RoleEntity] = Field(title="角色列表", default_factory=list)
    personal_profile: str | None = Field(title="个人简介", default=None)
    wecom_number: str | None = Field(title="企业微信号", default=None)
    personal_advantage: str | None = Field(title="个人优势", default=None)
    personal_photo: list[dict[str, Any]] | None = Field(title="个人照片", default_factory=list)
    last_operator: str | None = Field(title="最后操作人", default=None)
    current_role_id: int | None = Field(title="当前选择的角色ID", default=None)

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def process_password(cls, values):
        """
        处理密码：生成密码哈希
        """
        if isinstance(values, dict):
            password = values.get("password")
            if password and isinstance(password, str):
                # 生成密码哈希
                values["password_hash"] = hash_password(password)

        return values

    def add_roles_info(self, role_id_list, role_info):
        """
        添加关联角色
        :param role_id_list:
        :param role_info:
        :return:
        """
        # 如果roles是None，初始化为空列表
        if self.roles is None:
            self.roles = []

        for role_id in role_id_list:
            role_entity = role_info.get(role_id)
            if role_entity:
                self.roles.append(role_entity)

    def permission_check(self):
        if self.entity_id == ADMIN_USER_ID or self.username == ADMIN_USERNAME:
            raise PermissionDeniedError(message="超级管理员用户无法删除或编辑")

    @computed_field
    @property
    def permissions(self) -> dict[str, int]:
        """
        计算当前角色的权限
        如果指定了current_role_id，则返回该角色的权限
        否则返回所有角色权限的并集
        """
        if not self.roles:
            return {}

        if self.current_role_id:
            # 返回指定角色的权限
            for role in self.roles:
                if role.entity_id == self.current_role_id:
                    return role.permissions or {}
            return {}
        # 返回所有角色权限的并集
        all_permissions: dict[str, int] = {}
        for role in self.roles:
            if role.permissions:
                for perm_key, perm_level in role.permissions.items():
                    # 如果权限已存在，取更高的权限级别
                    if perm_key in all_permissions:
                        all_permissions[perm_key] = max(all_permissions[perm_key], perm_level)
                    else:
                        all_permissions[perm_key] = perm_level
        return all_permissions

    @computed_field
    @property
    def current_role(self) -> RoleEntity | None:
        """
        获取当前选择的角色
        """
        if not self.current_role_id or not self.roles:
            return None

        for role in self.roles:
            if role.entity_id == self.current_role_id:
                return role
        return None

    def has_permission(self, permission_name: str, required_level: int = 1) -> bool:
        """检查用户是否有特定权限"""
        user_permissions = self.permissions
        user_level = user_permissions.get(permission_name, 0)
        return user_level >= required_level

    def has_role(self, role_id: int) -> bool:
        """检查用户是否有指定角色"""
        if not self.roles:
            return False
        return any(role.entity_id == role_id for role in self.roles)

    def set_current_role(self, role_id: int) -> bool:
        """设置当前角色"""
        if self.has_role(role_id):
            self.current_role_id = role_id
            return True
        return False
