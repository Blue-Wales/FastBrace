#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : department_request.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 部门相关请求体模型
"""

from pydantic import BaseModel, Field

from api.request_body.page_request import PageRequest


class CreateDepartment(BaseModel):
    """创建部门请求体"""

    name: str = Field(..., description="部门名称")
    parent_id: int = Field(0, description="父部门ID，0表示根部门")


class UpdateDepartment(BaseModel):
    """更新部门请求体"""

    name: str | None = Field(None, description="部门名称")


class GetDepartmentUsers(PageRequest):
    """获取部门用户请求体"""

    dept_id: int = Field(..., description="部门ID")
    name: str | None = Field(None, description="用户名，用于筛选")
    mobile: str | None = Field(None, description="手机号，用于筛选")


class EditDepartmentUsers(BaseModel):
    """编辑部门用户关系请求体"""

    user_ids: list[int] = Field(..., description="用户ID列表")
