#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : base.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 基础响应模型
"""

from typing import Any

from pydantic import BaseModel, Field


class BaseResModel(BaseModel):
    """基础返回信息模型"""

    result: Any = Field(title="结果")
