#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : department_response.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 部门相关响应体模型
"""

from pydantic import BaseModel, Field


class DepartmentInfoResponse(BaseModel):
    """部门信息响应体"""

    dept_id: int = Field(title="部门ID", coerce_numbers_to_str=True, alias="entity_id")
    name: str = Field(title="部门名称")

    class Config:
        populate_by_name = True


class UpdateDepartmentResponse(DepartmentInfoResponse):
    """更新部门信息响应体"""

    pass


class CreateDepartmentResponse(DepartmentInfoResponse):
    """创建部门信息响应体"""

    pass


class DepartmentTreeResponse(BaseModel):
    """部门树响应体"""

    dept_id: int = Field(title="部门ID", coerce_numbers_to_str=True, alias="entity_id")
    name: str = Field(title="部门名称")
    children: list["DepartmentTreeResponse"] = Field(default_factory=list, title="子部门")

    class Config:
        populate_by_name = True


# 解决循环引用问题
DepartmentTreeResponse.model_rebuild()


class DepartmentUserResponse(BaseModel):
    """部门用户响应体"""

    user_id: str = Field(title="用户ID")
    name: str = Field(title="用户名")
    mobile: str = Field(title="手机号")
    email: str = Field(title="邮箱")
    avatar: str = Field(title="头像")
    status: int = Field(title="状态")
    is_leader: int = Field(title="是否部门负责人")
