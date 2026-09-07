#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : enum_var.py
@Author  : bright
@Date    : 2026-08-22
"""

from enum import Enum

from infrastructure.utils.custom_enum import BaseCodeLabelEnum


class BeanScope(Enum):
    """
    Bean工厂生成方式类型
    """

    SINGLETON = "singleton"

    PROTOTYPE = "prototype"


class ErrorCode(Enum):
    """
    错误码枚举（对齐 HTTP 状态码语义，保持唯一）
    """

    internal_error = 500  # 服务器内部错误

    file_upload_error = 415  # 文件上传失败

    api_request_error = 502  # api请求失败

    not_found_error = 404  # 资源不存在

    delete_error = 409  # 删除失败

    duplicate_entry_error = 422  # 重复数据

    authorization_error = 401  # 授权失败

    status_error = 412  # 状态错误

    invalid_input_error = 400  # 输入不合法

    permission_denied_error = 403  # 权限不足或不允许操作的资源

    function_unable_error = 501  # 功能不可用

    not_allowed_operation_error = 405  # 不允许的操作


class FileType(Enum):
    """
    文件类型编码对照表
    """

    personal_avatar = 1  # 个人头像
    personal_photo = 2  # 个人照片
    personal_qr_code = 3  # 个人二维码
    markdown_file = 19  # markdown文件


class Permissions(Enum):
    """
    权限类型
    """

    DASHBOARD = "Dashboard"
    USER_MANAGE = "UserManage"

    ACCOUNT = "UserManage.Account"
    ROLE = "UserManage.Role"
    DEPARTMENT = "UserManage.Department"


class PermissionLevel(BaseCodeLabelEnum):
    """
    权限等级
    """

    VIEW = (1, "查看")
    EDIT = (2, "操作")
    EXPORT = (3, "导出")


class LangCode(Enum):
    """
    语言类型编码
    """

    zh_CN = "zh_CN"
    en_US = "en_US"
