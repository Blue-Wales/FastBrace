#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : department.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import BIGINT

from infrastructure.utils.database import Base


class Department(Base):
    """
    部门数据模型类
    """

    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(BIGINT, unique=True, index=True, nullable=False, comment="实体id")
    name = Column(String(50), unique=True, nullable=False, comment="部门名称")


class DepartmentClosure(Base):
    """
    部门层级深度模型类
    """

    __tablename__ = "department_closure"
    ancestor = Column(BIGINT, primary_key=True, comment="祖先部门ID(实体id)", default="1")
    descendant = Column(BIGINT, primary_key=True, comment="后代部门ID(实体id)")
    depth = Column(Integer, nullable=False)
