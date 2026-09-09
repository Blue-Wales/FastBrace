#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : custom_enum.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

from enum import Enum


class BaseCodeLabelEnum(Enum):
    """
    支持 code-label 结构的枚举基类

    特性包含：
    1. 自动将元组第一个元素作为value(code)
    2. 自动附加label属性
    3. 提供根据code获取label的类方法
    """

    def __new__(cls, code: int, label: str):
        # 创建枚举成员时自动处理元组参数
        obj = object.__new__(cls)
        obj._value_ = code
        obj.label = label
        return obj

    @classmethod
    def get_name(cls, code: int) -> str:
        """
        通过code获取对应的中文标签
        当code不存在时返回"未知类型"
        """
        member = cls._value2member_map_.get(code)
        return member.label if member else "未知类型"
