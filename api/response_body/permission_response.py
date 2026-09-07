#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : permission_response.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 权限相关响应体模型
"""

from pydantic import BaseModel, Field


class PermissionTreeNodeResponse(BaseModel):
    """权限树节点响应"""

    entity_id: int = Field(title="实体ID")
    name: str = Field(title="节点名称")
    code: str = Field(title="节点编码")
    description: str | None = Field(title="节点描述")
    resource_type: str = Field(title="资源类型")
    parent_id: int | None = Field(title="父节点ID")
    depth: int = Field(title="深度")
    level: int = Field(title="级别")
    available_levels: list[int] = Field(title="可用的权限级别")
    selected_levels: list[int] = Field(title="已选择的权限级别")
    children: list["PermissionTreeNodeResponse"] | None = Field(
        title="子节点", default_factory=list
    )

    class Config:
        from_attributes = True


class DetailedPermissionNodeResponse(BaseModel):
    """细粒度权限节点响应"""

    entity_id: int = Field(title="实体ID")
    name: str = Field(title="节点名称")
    code: str = Field(title="节点编码")
    description: str | None = Field(title="节点描述")
    resource_type: str = Field(title="资源类型")
    parent_id: int | None = Field(title="父节点ID")
    depth: int = Field(title="深度")
    level: int = Field(title="级别")
    permission_level: int = Field(title="权限级别")
    # module级别使用children
    children: list["DetailedPermissionNodeResponse"] | None = Field(
        title="子节点", default_factory=list
    )
    # action级别使用action字段
    action: list["DetailedPermissionNodeResponse"] | None = Field(
        title="动作子节点", default_factory=list
    )

    class Config:
        from_attributes = True


class PermissionSummaryResponse(BaseModel):
    """权限摘要响应"""

    module_code: str = Field(title="模块代码")
    module_name: str = Field(title="模块名称")
    permissions: str = Field(title="权限描述")


class SavePermissionResponse(BaseModel):
    """保存权限响应"""

    success: bool = Field(title="是否成功")
    message: str = Field(title="消息")
    role_id: int = Field(title="角色ID")


class ValidatePermissionResponse(BaseModel):
    """验证权限响应"""

    has_permission: bool = Field(title="是否有权限")
    module_code: str = Field(title="模块代码")
    required_level: int = Field(title="需要的权限级别")
    user_level: int = Field(title="用户权限级别")


class PermissionLevelInfo(BaseModel):
    """权限级别信息"""

    level: int = Field(title="级别")
    name: str = Field(title="级别名称")
    description: str = Field(title="级别描述")


class PermissionSystemInfoResponse(BaseModel):
    """权限系统信息响应"""

    permission_levels: list[PermissionLevelInfo] = Field(title="权限级别信息")
    module_count: int = Field(title="模块数量")
    action_count: int = Field(title="动作数量")

    class Config:
        from_attributes = True
