#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : common_response.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 通用响应体模型
"""

from pydantic import BaseModel, Field


class FileResponse(BaseModel):
    """文件信息响应体"""

    file_name: str = Field(title="文件名称")
    file_path: str = Field(title="文件路径")
    extra_info: str | None = Field(title="文件附加信息", default=None)


class LabelTypeResponse(BaseModel):
    """标签类型响应体"""

    code: int = Field(title="标签类型编码")
    name: str = Field(title="标签类型名称")
