#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : role_response.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 角色相关响应体模型
"""

from pydantic import BaseModel, Field


class RoleInfoResponse(BaseModel):
    """角色信息响应体"""

    role_id: int = Field(title="角色ID", coerce_numbers_to_str=True, alias="entity_id")
    code: str = Field(title="角色唯一编码")
    name: str = Field(title="角色名称")
    permissions: dict = Field(title="权限配置信息")


class RoleTreeResponse(BaseModel):
    """角色树响应体"""

    role_id: int = Field(title="角色ID", coerce_numbers_to_str=True, alias="entity_id")
    code: str = Field(title="角色唯一编码")
    name: str = Field(title="角色名称")
    child_role: list["RoleTreeResponse"] | None = Field(title="子角色", default_factory=list)


RoleTreeResponse.model_rebuild()
