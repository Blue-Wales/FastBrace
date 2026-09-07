#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : response_model_generator.py
@Author  : bright
@Date    : 2026-08-22
"""

from typing import TypeVar

from pydantic import BaseModel, Field, create_model

T = TypeVar("T")


class ResponseModelFactory:
    """
    响应模型工厂类，用于创建标准格式的响应模型
    """

    @classmethod
    def create_response_model(
        cls,
        data_class: type,
        name: str | None = None,
        code_default: int = 200,
        message_default: str = "success",
        code_description: str = "状态码",
        message_description: str = "状态信息",
        data_description: str = "返回数据",
    ) -> type[BaseModel]:
        """
        创建标准响应模型类

        Args:
            data_class: 响应数据类型
            name: 响应模型类名，为None时将基于data_class名称自动生成
            code_default: 状态码默认值
            message_default: 状态信息默认值
            code_description: 状态码描述
            message_description: 状态信息描述
            data_description: 返回数据描述

        Returns:
            创建的响应模型类
        """
        # 如果未提供类名，则基于data_class自动生成
        if name is None:
            data_class_name = getattr(data_class, "__name__", str(data_class))
            name = f"{data_class_name}ResponseModel"

        # 使用pydantic的create_model函数创建模型
        return create_model(
            name,
            code=(int, Field(default=code_default, description=code_description)),
            message=(str, Field(default=message_default, description=message_description)),
            data=(data_class, Field(description=data_description)),
            __doc__=f"动态生成的响应模型，数据类型: {data_class}",
        )


# 便捷函数接口
def generate_response_model(
    data_class: type,
    name: str | None = None,
    code_default: int = 200,
    message_default: str = "success",
) -> type[BaseModel]:
    """
    生成标准响应模型

    Args:
        data_class: 响应数据类型
        name: 响应模型类名，为None时将基于data_class名称自动生成
        code_default: 状态码默认值
        message_default: 状态信息默认值

    Returns:
        生成的响应模型类
    """
    return ResponseModelFactory.create_response_model(
        data_class=data_class, name=name, code_default=code_default, message_default=message_default
    )


class PagedResponseModelFactory(ResponseModelFactory):
    """分页响应模型工厂类"""

    @classmethod
    def create_paged_response_model(
        cls,
        item_class: type,
        name: str | None = None,
        code_default: int = 200,
        message_default: str = "success",
    ) -> type[BaseModel]:
        """
        创建分页响应模型

        Args:
            item_class: 分页项类型
            name: 模型类名
            code_default: 状态码默认值
            message_default: 状态信息默认值

        Returns:
            创建的分页响应模型类
        """
        # 创建分页数据模型的名称
        page_data_name = f"{getattr(item_class, '__name__', 'Item')}PagedData"

        # 创建分页数据模型
        paged_data_class = create_model(
            page_data_name,
            total=(int, Field(default=0, description="总记录数")),
            page=(int, Field(default=1, description="当前页码")),
            page_size=(int, Field(default=10, description="每页记录数", gt=0)),
            items=(list[item_class], Field(default_factory=list, description="记录列表")),
            pages=(int, Field(default=0, description="总页数")),
        )

        # 使用基类方法创建最终响应模型
        return cls.create_response_model(
            data_class=paged_data_class,
            name=name or f"{getattr(item_class, '__name__', 'Item')}PagedResponseModel",
            code_default=code_default,
            message_default=message_default,
        )


# 便捷分页响应模型生成函数
def generate_paged_response_model(
    item_class: type,
    name: str | None = None,
    code_default: int = 200,
    message_default: str = "success",
) -> type[BaseModel]:
    """
    生成分页响应模型

    Args:
        item_class: 分页项类型
        name: 响应模型类名
        code_default: 状态码默认值
        message_default: 状态信息默认值

    Returns:
        生成的分页响应模型类
    """
    return PagedResponseModelFactory.create_paged_response_model(
        item_class=item_class, name=name, code_default=code_default, message_default=message_default
    )


# 新增列表响应模型工厂类
class ListResponseModelFactory(ResponseModelFactory):
    """列表响应模型工厂类"""

    @classmethod
    def create_list_response_model(
        cls,
        item_class: type,
        name: str | None = None,
        code_default: int = 200,
        message_default: str = "success",
        data_description: str = "返回数据列表",
    ) -> type[BaseModel]:
        """
        创建列表响应模型

        Args:
            item_class: 列表项数据类型
            name: 模型类名，为空时自动生成
            code_default: 状态码默认值
            message_default: 状态信息默认值
            data_description: 数据字段描述

        Returns:
            列表响应模型类
        """
        # 自动生成模型名称
        if name is None:
            item_name = getattr(item_class, "__name__", str(item_class))
            name = f"{item_name}ListResponseModel"

        # 创建列表数据类型
        list_data_class = create_model(
            f"{name}Data",
            items=(list[item_class], Field(default_factory=list, description="数据列表")),
        )

        # 调用基类创建响应模型
        return super().create_response_model(
            data_class=list_data_class,
            name=name,
            code_default=code_default,
            message_default=message_default,
            data_description=data_description,
        )


def generate_list_response_model(
    item_class: type,
    name: str | None = None,
    code_default: int = 200,
    message_default: str = "success",
    data_description: str = "返回数据列表",
) -> type[BaseModel]:
    """
    生成列表响应模型

    Args:
        item_class: 列表项数据类型
        name: 模型类名，为空时自动生成
        code_default: 状态码默认值
        message_default: 状态信息默认值
        data_description: 数据字段描述
    Returns:
            列表响应模型类
    """
    return ListResponseModelFactory.create_list_response_model(
        item_class=item_class,
        name=name,
        code_default=code_default,
        message_default=message_default,
        data_description=data_description,
    )
