#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : role.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 角色数据模型（含闭包表）
"""

from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.dialects.mysql import BIGINT

from infrastructure.utils.database import Base

ADMIN_ROLE_ID = 1
ADMIN_ROLE_NAME = "超级管理员"
ADMIN_ROLE_CODE = "super_admin"


class Role(Base):
    """
    角色数据模型类
    """

    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(BIGINT, unique=True, index=True, nullable=False, comment="实体id")
    code = Column(String(64), unique=True, nullable=False, comment="角色唯一编码")
    name = Column(String(50), unique=True, nullable=False, comment="角色名称")
    permissions = Column(JSON, comment="权限配置信息")


class RoleClosure(Base):
    """
    角色层级闭包表模型 用于存储角色间的层级关系

    属性:
        __tablename__ (str): 数据库表名，对应'role_closure'表
        ancestor (Column): 祖先角色ID（复合主键），关联roles表的id
        descendant (Column): 后代角色ID（复合主键），关联roles表的id
        depth (Column): 层级深度，表示两个角色间的继承层级数

    方法:
        __repr__: 返回对象的格式化字符串表示
    """

    __tablename__ = "role_closure"
    ancestor = Column(BIGINT, primary_key=True, comment="祖先角色ID(实体id)", default="1")
    descendant = Column(BIGINT, primary_key=True, comment="后代角色ID(实体id)")
    depth = Column(Integer, nullable=False)
