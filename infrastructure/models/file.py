#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : file.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

from sqlalchemy import BIGINT, Column, Integer, String

from infrastructure.utils.database import Base


class File(Base):
    __tablename__ = "file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    master_id = Column(BIGINT, nullable=False, index=True, comment="文件所属实体的id")
    file_type = Column(Integer, nullable=False, comment="文件类型")
    file_path = Column(String(2048), nullable=False, comment="文件路径")
    file_name = Column(String(255), nullable=False, comment="文件名称")
    extra_info = Column(String(2048), nullable=True, comment="扩展信息")
