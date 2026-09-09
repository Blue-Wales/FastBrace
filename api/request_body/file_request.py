#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : file_request.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 文件相关请求体模型
"""

from fastapi import UploadFile
from pydantic import BaseModel, Field


class UploadFileRequest(BaseModel):
    """文件上传请求体"""

    file: UploadFile = Field(title="文件")
    file_type: str = Field(title="文件类型")


class FileRequest(BaseModel):
    """文件信息请求体"""

    file_name: str = Field(title="文件名称")
    file_path: str = Field(title="文件路径")
    extra_info: str | None = Field(title="附加信息", default=None)
