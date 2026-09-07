#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : user.py
@Author  : bright
@Date    : 2026-08-22
"""

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import BIGINT

from infrastructure.utils.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(BIGINT, unique=True, index=True, comment="实体id", nullable=False)
    username = Column(String(64), unique=True, comment="用户名", nullable=False)
    name = Column(String(64), comment="姓名", nullable=False)
    mobile = Column(String(20), comment="手机号", nullable=False)
    password_hash = Column(String(255), comment="密码哈希", nullable=False)
    gender = Column(TINYINT, server_default=text("0"), comment="性别(2：女，1：男, 0: 未定义)")
    email = Column(String(120), comment="邮箱", nullable=False)
    status = Column(TINYINT, server_default=text("1"), comment="状态(1 已激活，2：已禁用)")
    create_time = Column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), comment="Column(创建时间"
    )
    update_time = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="Column(修改时间",
    )
    nick_name = Column(String(64), nullable=True, comment="昵称")
    personal_profile = Column(String(255), nullable=True, comment="个人简介")
    personal_advantage = Column(String(255), nullable=True, comment="个人优势")
    wecom_number = Column(String(64), comment="企业微信号")
    last_operator = Column(String(64), comment="最后操作人")

    __table_args__ = (UniqueConstraint("mobile", "status", name="uix_mobile_status"),)


class UserRoleRelations(Base):
    __tablename__ = "user_role_relations"

    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, comment="用户id(用户实体id)")
    role_id = Column(BIGINT, comment="角色id(角色实体id)")
    create_time = Column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"), comment="Column(创建时间"
    )
