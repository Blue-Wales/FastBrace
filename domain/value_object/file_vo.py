#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : file_vo.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 文件值对象
"""

from pydantic import BaseModel, Field


class FileVO(BaseModel):
    """
    文件对象
    """

    master_id: int | None = Field(description="资源id")
    file_path: str = Field(description="文件路径")
    file_name: str = Field(description="文件名称")
    file_type: int = Field(description="文件类型")
    extra_info: str | None = Field(description="文件附加信息", default=None)

    class Config:
        from_attributes = True
        # 允许任意类型转换
        arbitrary_types_allowed = True
