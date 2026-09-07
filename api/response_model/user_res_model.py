#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : user_res_model.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 用户相关响应模型
"""

from typing import Any

from pydantic import BaseModel, Field

from api.response_model.common_res_model import FileResModel


class UserItemModel(BaseModel):
    """用户列表信息响应模型"""

    name: str = Field(title="用户名")
    nick_name: str | None = Field(title="昵称", default=None)
    mobile: str = Field(title="手机号")
    user_id: str = Field(title="用户id", coerce_numbers_to_str=True)
    update_time: str | None = Field(title="修改时间", default=None)
    last_operator: str | None = Field(title="最后操作人", default=None)
    roles: list[str] = Field(title="角色名称列表")
    status: bool = Field(title="状态", default=True)


class UserRoleModel(BaseModel):
    """用户角色信息响应模型"""

    role_id: int = Field(title="角色ID", coerce_numbers_to_str=True)
    code: str = Field(title="角色唯一编码")
    name: str = Field(title="角色名称")
    permissions: dict[str, Any] | None = Field(title="权限", default=None)


class UserInfoModel(BaseModel):
    """用户详细信息响应模型"""

    username: str = Field(title="用户名")
    name: str | None = Field(title="姓名", default=None)
    nick_name: str | None = Field(title="昵称", default=None)
    mobile: str | None = Field(title="手机号", default=None)
    email: str | None = Field(title="邮箱", default=None)
    user_id: str = Field(title="用户id", coerce_numbers_to_str=True, alias="entity_id")
    gender: int | None = Field(title="性别", default=None)
    personal_profile: str | None = Field(title="介绍", default=None)
    personal_advantage: str | None = Field(title="优势", default=None)
    personal_avatar: list[FileResModel] = Field(title="头像", default_factory=list)
    personal_qr_code: list[FileResModel] = Field(title="二维码", default_factory=list)
    personal_photo: list[FileResModel] = Field(title="缩略头像", default_factory=list)
    wecom_number: str | None = Field(title="企业微信号", default=None)
    update_time: str | None = Field(title="修改时间", default=None)
    last_operator: str | None = Field(title="最后操作人", default=None)
    roles: list[UserRoleModel] = Field(title="角色id名称列表")
    status: bool = Field(title="状态", default=True)


class CurrentUserRoleModel(BaseModel):
    """当前用户角色信息响应模型"""

    role_id: int = Field(title="角色ID", coerce_numbers_to_str=True, alias="entity_id")
    code: str = Field(title="角色唯一编码")
    name: str = Field(title="角色名称")
    permissions: dict = Field(title="权限")


class CurrentUserModel(BaseModel):
    """当前用户信息响应模型"""

    name: str | None = Field(title="用户名", default=None)
    nick_name: str | None = Field(title="昵称", default=None)
    mobile: str | None = Field(title="手机号", default=None)
    user_id: str = Field(title="用户id", coerce_numbers_to_str=True, alias="entity_id")
    personal_avatar: list[FileResModel] = Field(title="头像", default_factory=list)
    roles: list[CurrentUserRoleModel] = Field(title="角色列表")


class UserResModel(BaseModel):
    """用户名称响应模型"""

    user_id: str = Field(title="用户id")
    name: str = Field(title="用户名")


class LoginTokenModel(BaseModel):
    """登录令牌响应模型"""

    code: int = Field(title="状态码")
    access_token: str = Field(title="访问令牌")
    refresh_token: str = Field(title="刷新令牌")


class AccessTokenModel(BaseModel):
    """访问令牌响应模型"""

    code: int = Field(title="状态码")
    access_token: str = Field(title="访问令牌")
    expires_in: int = Field(title="过期时间")


class UserRolesModel(BaseModel):
    """用户角色响应模型"""

    code: int = Field(title="状态码")
    roles: list[int] = Field(title="角色id列表")


class LogoutModel(BaseModel):
    """退出登录响应模型"""

    code: int = Field(title="状态码")
    message: str = Field(title="提示信息")


class CurrentRoleModel(BaseModel):
    """当前角色响应模型"""

    code: int = Field(title="状态码")
    role_id: str = Field(title="角色ID")
    role_name: str = Field(title="角色名称")
    permissions: dict | None = Field(title="权限配置", default=None)
