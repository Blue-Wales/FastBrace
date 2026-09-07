#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : page_request.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 通用分页请求体模型
"""

from pydantic import BaseModel, Field


class PageRequest(BaseModel):
    """通用分页请求体"""

    page: int | None = Field(default=None, description="当前页码", gt=0)
    page_size: int | None = Field(default=None, description="每页记录数", gt=0)
