#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : json_response.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 基础 JSON 响应体模型
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class BaseResponseModel(BaseModel):
    """基础返回体"""

    result: Any = Field(title="结果")


class ResponseModel(BaseModel):
    """标准返回体"""

    code: int = Field(default=200, title="状态码")
    message: str = Field(default="success", title="状态信息")
    data: dict = Field(default_factory=dict, title="返回数据")


class ResponseListModel(BaseModel):
    """列表返回体"""

    code: int = Field(default=200, title="状态码")
    message: str = Field(default="success", title="状态信息")
    data: list = Field(default_factory=list, title="返回数据列表")


class PagedDataModel(BaseModel):
    """分页数据模型"""

    total: int = Field(default=0, title="总记录数")
    page: int = Field(default=1, title="当前页码")
    page_size: int = Field(default=10, title="每页记录数", gt=0)
    items: list = Field(default_factory=list, title="返回数据")
    pages: int = Field(default=0, title="总页数")

    @field_validator("pages", mode="before")
    def generate_pages(cls, _, values):
        if values.get("total") and values.get("page_size"):
            return int(values.get("total") / values.get("page_size")) + 1
        return 0


class PaginationResponseModel(BaseModel):
    """分页专用返回体"""

    code: int = Field(default=200, title="状态码")
    message: str = Field(default="success", title="状态信息")
    data: PagedDataModel = Field(default_factory=PagedDataModel, title="返回数据")
