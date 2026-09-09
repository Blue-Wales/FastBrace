#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : permission_resources.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 权限资源模型
"""

from sqlalchemy import BIGINT, Column, Integer, String, text
from sqlalchemy.orm import relationship

from infrastructure.utils.database import Base


class PermissionResources(Base):
    """
    权限资源模型
    """

    __tablename__ = "permission_resources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(BIGINT, nullable=False, index=True, unique=True, comment="权限资源id")
    name = Column(String(255), nullable=False, comment="权限资源名称")
    code = Column(String(255), nullable=False, comment="权限资源编码", index=True, unique=True)
    description = Column(String(255), nullable=True, comment="权限资源描述")
    resource_type = Column(String(32), nullable=False, comment="权限资源类型")
    parent_id = Column(
        BIGINT,
        nullable=True,
        index=True,
        comment="父权限资源id",
    )
    depth = Column(Integer, nullable=False, comment="权限资源深度", server_default=text("1"))
    level = Column(Integer, nullable=False, comment="权限资源级别", server_default=text("1"))
    child_permissions = relationship(
        "PermissionResources",
        primaryjoin="PermissionResources.entity_id == PermissionResources.parent_id",
        foreign_keys="PermissionResources.parent_id",
        uselist=True,
        back_populates="parent_permission",
        viewonly=True,
    )
    parent_permission = relationship(
        "PermissionResources",
        primaryjoin="PermissionResources.parent_id == PermissionResources.entity_id",
        foreign_keys="PermissionResources.parent_id",
        remote_side="PermissionResources.entity_id",
        uselist=False,
        back_populates="child_permissions",
        viewonly=True,
    )
