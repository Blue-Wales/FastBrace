#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : common_res_model.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 通用响应模型
"""

from pydantic import BaseModel, Field


class CommonItemResModel(BaseModel):
    """通用信息响应模型"""

    code: int = Field(title="类型编码")
    name: str = Field(title="类型名称")


class FileResModel(BaseModel):
    """文件信息响应模型"""

    file_name: str = Field(title="文件名称")
    file_path: str = Field(title="文件路径")


class LabelTypeResModel(BaseModel):
    """标签类型响应模型"""

    code: int = Field(title="标签类型编码")
    name: str = Field(title="标签类型名称")
