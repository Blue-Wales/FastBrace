#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : permission_request.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 权限相关请求体模型
"""

from pydantic import BaseModel, Field


class SaveRolePermissionsRequest(BaseModel):
    """保存角色权限请求体"""

    role_id: int = Field(title="角色ID", description="要设置权限的角色ID")
    permissions: dict[str, list[int]] = Field(
        title="权限配置", description="模块权限配置，格式为 {模块代码: [权限级别列表]}"
    )


class GetRolePermissionsRequest(BaseModel):
    """获取角色权限请求体"""

    role_id: int = Field(title="角色ID", description="要获取权限的角色ID")


class GetDetailedPermissionsRequest(BaseModel):
    """获取细粒度权限请求体"""

    role_id: int = Field(title="角色ID", description="要获取细粒度权限的角色ID")


class ValidatePermissionRequest(BaseModel):
    """验证权限请求体"""

    module_code: str = Field(title="模块代码", description="要验证的模块代码")
    required_level: int = Field(
        title="需要的权限级别", description="需要的权限级别（1=查看，2=操作，3=导出）"
    )
    user_permissions: dict[str, list[int]] = Field(
        title="用户权限", description="用户当前的权限配置"
    )
