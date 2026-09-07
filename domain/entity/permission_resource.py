#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : permission_resource.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 权限资源实体类
"""

from typing import Optional

from pydantic import Field

from domain.entity.base import Entity


class PermissionResourceEntity(Entity):
    """权限资源实体"""

    name: str = Field(title="权限资源名称")
    code: str = Field(title="权限资源编码")
    description: str | None = Field(title="权限资源描述", default=None)
    resource_type: str = Field(title="权限资源类型")  # module/action
    parent_id: int | None = Field(title="父权限资源id", default=None)
    depth: int = Field(title="权限资源深度", default=1)
    level: int = Field(title="权限资源级别", default=1)

    # 关联属性
    children: list["PermissionResourceEntity"] | None = Field(
        title="子权限资源", default_factory=list
    )
    parent: Optional["PermissionResourceEntity"] = Field(title="父权限资源", default=None)

    class Config:
        from_attributes = True


class PermissionTreeNode(Entity):
    """权限树节点"""

    name: str = Field(title="节点名称")
    code: str = Field(title="节点编码")
    description: str | None = Field(title="节点描述", default=None)
    resource_type: str = Field(title="资源类型")
    parent_id: int | None = Field(title="父节点ID", default=None)
    depth: int = Field(title="深度", default=1)
    level: int = Field(title="级别", default=1)

    # 权限相关
    available_levels: list[int] = Field(title="可用的权限级别", default_factory=list)
    selected_levels: list[int] = Field(title="已选择的权限级别", default_factory=list)

    # 子节点
    children: list["PermissionTreeNode"] | None = Field(title="子节点", default_factory=list)

    class Config:
        from_attributes = True


class DetailedPermissionNode(Entity):
    """细粒度权限节点"""

    name: str = Field(title="节点名称")
    code: str = Field(title="节点编码")
    description: str | None = Field(title="节点描述", default=None)
    resource_type: str = Field(title="资源类型")
    parent_id: int | None = Field(title="父节点ID", default=None)
    depth: int = Field(title="深度", default=1)
    level: int = Field(title="级别", default=1)

    # 权限状态
    permission_level: int = Field(title="权限级别", default=0)

    # 子节点 - module级别使用children
    children: list["DetailedPermissionNode"] | None = Field(title="子节点", default_factory=list)
    # action级别使用action字段
    action: list["DetailedPermissionNode"] | None = Field(title="动作子节点", default_factory=list)

    class Config:
        from_attributes = True
