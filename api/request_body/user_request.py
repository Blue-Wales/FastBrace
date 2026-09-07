#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : user_request.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 用户相关请求体模型
"""

import datetime

from pydantic import BaseModel, Field, computed_field, field_validator

from api.request_body.file_request import FileRequest
from api.request_body.page_request import PageRequest
from infrastructure.utils.rsa_utils import rsa_password_validator


class EditUserRequest(BaseModel):
    """编辑用户请求体"""

    nick_name: str | None = Field(title="昵称", default=None)
    name: str | None = Field(title="姓名", default=None)
    mobile: str | None = Field(title="手机号", default=None)
    username: str | None = Field(title="用户名", default=None)
    email: str | None = Field(title="邮箱", default=None)
    roles: list[int] | None = Field(title="角色id列表", default=None)
    dept_ids: list[int] | None = Field(title="部门id列表", default=None)
    gender: int | None = Field(title="性别", default=None, ge=1, le=2)
    personal_profile: str | None = Field(title="个人简介", default=None)
    personal_advantage: str | None = Field(title="个人优势", default=None)
    personal_avatar: list[FileRequest] | None = Field(title="个人头像", default_factory=list)
    personal_photo: list[FileRequest] | None = Field(title="个人形象", default_factory=list)
    personal_qr_code: list[FileRequest] | None = Field(title="个人二维码", default_factory=list)
    wecom_number: str | None = Field(title="企业微信号", default=None)
    status: bool | None = Field(title="状态(启用/停用)", default=None)

    @computed_field
    def update_time(self) -> datetime.datetime:
        return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))


class CreateUserRequest(BaseModel):
    """新增用户请求体"""

    nick_name: str = Field(title="昵称")
    name: str = Field(title="姓名")
    mobile: str = Field(title="手机号")
    username: str = Field(title="用户名")
    email: str = Field(title="邮箱")
    password: str | None = Field(title="密码", default=None)
    roles: list[int] = Field(title="角色id列表", default_factory=list)
    dept_ids: list[int] = Field(title="部门id列表", default_factory=list)
    gender: int = Field(title="性别", ge=1, le=2)
    personal_profile: str | None = Field(title="个人简介", default=None)
    personal_advantage: str | None = Field(title="个人优势", default=None)
    personal_avatar: list[FileRequest] | None = Field(title="个人头像", default_factory=list)
    personal_photo: list[FileRequest] | None = Field(title="个人形象", default_factory=list)
    personal_qr_code: list[FileRequest] | None = Field(title="个人二维码", default_factory=list)
    wecom_number: str | None = Field(title="企业微信号", default=None)
    status: bool | None = Field(title="状态(启用/停用)", default=None)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证并自动解密密码"""
        return rsa_password_validator(v)


class EditUserPasswordRequest(BaseModel):
    """修改用户密码请求体"""

    old_password: str = Field(title="旧密码")
    password: str = Field(title="新密码")
    password_confirm: str = Field(title="确认密码")

    @field_validator("old_password", "password", "password_confirm")
    @classmethod
    def validate_passwords(cls, v: str) -> str:
        """验证并自动解密所有密码字段"""
        return rsa_password_validator(v)


class LoginRequest(BaseModel):
    """登录请求模型 - 展示RSA密码字段的使用"""

    username: str = Field(title="用户名", description="用户登录名")
    password: str = Field(title="密码", description="支持明文或RSA加密密码，系统会自动解密")
    role_id: int | None = Field(title="角色ID", default=None, description="选择的角色ID（可选）")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证并自动解密密码"""
        return rsa_password_validator(v)


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求体"""

    refresh_token: str = Field(title="刷新token")


class GetUsersRequest(PageRequest):
    """分页获取用户列表请求体"""

    page: int = Field(default=1, description="页码", gt=0)
    page_size: int = Field(default=10, description="每页条数", gt=0, le=100)
    name: str | None = Field(default=None, description="用户名")
    mobile: str | None = Field(default=None, description="手机号")
    role_ids: list[int] | None = Field(default=None, description="角色ID列表")
    status: bool | None = Field(default=None, description="用户状态（true为激活）")


class GetUserNameListRequest(BaseModel):
    """获取用户名称列表请求体"""

    name: str | None = Field(default=None, description="用户名")


class EditUserStatusRequest(BaseModel):
    """修改用户状态请求体"""

    entity_id_list: list[int] = Field(title="用户id列表", alias="user_id_list")
    status: bool = Field(title="状态")


class RoleLoginRequest(BaseModel):
    """角色切换请求体"""

    role_id: int = Field(..., title="角色ID", description="要切换到的角色ID")


class CrmUpdateCustomerConsultantRequest(BaseModel):
    """更新客户顾问请求体"""

    mobile: str = Field(title="新顾问手机号")
    customer_id: int = Field(title="客户id")
    operation_consultant: str = Field(title="操作人名称")
    customer_mobile: str = Field(title="客户手机号")
    wechat: str = Field(title="客户微信")
    campus_id: str = Field(title="客户校区id")
    apartment_id: str = Field(title="公寓id")
    room_type_id: str = Field(title="房型id")
    name: str = Field(title="预定人名称")
    source_consultant_mobile: str = Field(title="原顾问手机号")
