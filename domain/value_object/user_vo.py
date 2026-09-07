#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : user_vo.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 用户值对象
"""

from typing import Any

from pydantic import BaseModel, Field


class UserSummaryVO(BaseModel):
    """
    用户摘要信息
    """

    entity_id: int = Field(title="用户id")
    name: str = Field(title="用户名")

    class Config:
        from_attributes = True


class UserMobileVO(UserSummaryVO):
    """
    顾问手机号
    """

    mobile: str = Field(title="手机号")


class UserInfoVO(BaseModel):
    """
    用户所属顾问信息
    """

    user_id: str = Field(title="顾问id", coerce_numbers_to_str=True, alias="entity_id")
    name: str = Field(title="姓名")
    gender: int | None = Field(title="性别(2：女，1：男, 0: 未定义)")
    nick_name: str | None = Field(title="昵称")
    personal_profile: str | None = Field(title="个人简介")
    personal_advantage: str | None = Field(title="个人优势")
    wecom_number: str | None = Field(title="企业微信号")
    personal_avatar: list[dict[str, Any]] | None = Field(title="头像", default_factory=list)
    personal_photo: list[dict[str, Any]] | None = Field(title="个人照片", default_factory=list)
    personal_qr_code: list[dict[str, Any]] | None = Field(title="二维码", default_factory=list)

    class Config:
        from_attributes = True



