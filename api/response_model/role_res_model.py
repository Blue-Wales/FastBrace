#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : role_res_model.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 角色相关响应模型
"""

from datetime import datetime

from pydantic import BaseModel, Field


class RoleInfoModel(BaseModel):
    """角色信息响应模型"""

    role_id: int = Field(title="角色ID", coerce_numbers_to_str=True)
    code: str = Field(title="角色唯一编码")
    name: str = Field(title="角色名称")
    permissions: dict = Field(title="权限配置信息")


class RoleUsersItemModel(BaseModel):
    """角色用户列表响应模型"""

    name: str = Field(title="用户名")
    nick_name: str = Field(title="昵称")
    mobile: str = Field(title="手机号")
    user_id: str = Field(title="用户id", coerce_numbers_to_str=True)
    modify_time: datetime = Field(title="修改时间")
    last_operator: str = Field(title="最后操作人")
    roles: list[str] = Field(title="角色名称列表")


class RoleTreeModel(BaseModel):
    """角色树响应模型"""

    role_id: int = Field(title="角色ID", coerce_numbers_to_str=True)
    code: str = Field(title="角色唯一编码")
    name: str = Field(title="角色名称")
    child_role: list[dict] = Field(title="子角色")
