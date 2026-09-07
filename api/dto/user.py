#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : user.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 用户 DTO 数据模型
"""

from pydantic import BaseModel, Field


class UserDTO(BaseModel):
    """用户数据传输对象"""

    entity_id: int = Field(title="用户id")
    name: str = Field(title="用户名")

    class Config:
        from_attributes = True
