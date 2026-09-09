#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : user_response.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 用户相关响应体模型
"""

from pydantic import BaseModel, Field, field_validator

from api.response_body.common_response import FileResponse


class UserItemResponse(BaseModel):
    """用户列表信息响应体"""

    name: str = Field(title="用户名")
    nick_name: str | None = Field(title="昵称", default=None)
    mobile: str = Field(title="手机号")
    user_id: str = Field(title="用户id", coerce_numbers_to_str=True, alias="entity_id")
    update_time: str | None = Field(title="修改时间", default=None)
    last_operator: str | None = Field(title="最后操作人", default=None)
    roles: list[str] = Field(title="角色名称列表")
    status: bool = Field(title="状态", default=True)

    @field_validator("roles", mode="before")
    @classmethod
    def roles_validator(cls, value):
        """将角色实体列表转换为角色名称列表"""
        return [role.get("name") for role in value]


    @field_validator("update_time", mode="before")
    @classmethod
    def update_time_validator(cls, value):
        """将时间格式化为 YYYY-MM-DD HH:MM:SS 字符串"""
        if value is not None:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return None


class UserRoleInfo(BaseModel):
    """用户角色信息响应体"""

    role_id: int = Field(title="角色ID", coerce_numbers_to_str=True, alias="entity_id")
    code: str = Field(title="角色唯一编码")
    name: str = Field(title="角色名称")
    permissions: dict = Field(title="权限")


class UserExtraInfoResponse(BaseModel):
    """用户额外信息响应体"""

    username: str = Field(title="用户名")
    name: str | None = Field(title="用户名")
    nick_name: str | None = Field(title="昵称")
    mobile: str | None = Field(title="手机号")
    email: str | None = Field(title="邮箱")
    user_id: str = Field(title="用户id", coerce_numbers_to_str=True, alias="entity_id")
    gender: int | None = Field(title="性别")
    personal_profile: str | None = Field(title="个人简介")
    personal_advantage: str | None = Field(title="个人优势")
    personal_avatar: list[FileResponse] | None = Field(title="个人头像", default_factory=list)
    personal_qr_code: list[FileResponse] | None = Field(title="个人二维码", default_factory=list)
    personal_photo: list[FileResponse] | None = Field(title="缩略头像", default_factory=list)
    wecom_number: str | None = Field(title="企业微信号", default=None)
    update_time: str | None = Field(title="修改时间", default=None)
    last_operator: str | None = Field(title="最后操作人", default=None)
    roles: list[UserRoleInfo] = Field(title="角色id名称列表")
    status: bool = Field(title="状态", default=True)

    @field_validator("update_time", mode="before")
    @classmethod
    def update_time_validator(cls, value):
        """将时间格式化为 YYYY-MM-DD HH:MM:SS 字符串"""
        if value is not None:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return None


class CurrentUserInfo(BaseModel):
    """当前用户信息响应体"""

    name: str | None = Field(title="用户名")
    nick_name: str | None = Field(title="昵称")
    mobile: str | None = Field(title="手机号")
    user_id: str = Field(title="用户id", coerce_numbers_to_str=True, alias="entity_id")
    personal_avatar: list[FileResponse] | None = Field(title="头像", default_factory=list)
    roles: list[UserRoleInfo] = Field(title="角色列表")


class UserResponse(BaseModel):
    """用户基础信息响应体"""

    user_id: int = Field(title="用户id", coerce_numbers_to_str=True, alias="entity_id")
    name: str = Field(title="用户名")
