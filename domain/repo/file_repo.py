#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : file_repo.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 文件仓储实现
"""

from sqlalchemy import tuple_

from domain.repo.base import BaseRepository
from domain.value_object.file_vo import FileVO
from infrastructure.core.container import repository_factory
from infrastructure.core.enum_var import BeanScope
from infrastructure.models.file import File


@repository_factory.autowire("file_repo", scope=BeanScope.PROTOTYPE.value)
class FileRepository(BaseRepository):
    """基于 SQLAlchemy 批量映射能力的文件仓储实现。"""

    async def save(self, file_vo_list):
        """使用 bulk mappings 批量写入文件关系。"""
        return self.db.bulk_insert_mappings(File, file_vo_list)

    async def get(self, master_id: int, file_types: list[int] | None = None):
        """组合主对象与可选文件类型条件查询。"""
        q = self.db.query(File).filter(File.master_id == master_id)
        if file_types:
            q = q.filter(File.file_type.in_(file_types))
        file_objs = q.all()
        return [self._to_entity(file_obj, FileVO) for file_obj in file_objs]

    async def get_multiple(self, master_ids: list[int], file_types: list[int] | None = None):
        """批量查询多个主对象的文件关系。"""
        q = self.db.query(File).filter(File.master_id.in_(master_ids))
        if file_types:
            q = q.filter(File.file_type.in_(file_types))
        file_objs = q.all()
        return [self._to_entity(file_obj, FileVO) for file_obj in file_objs]

    async def delete(self, pair_list: list[dict]):
        """使用复合 IN 条件批量删除文件关系。"""
        pairs = []
        for pair in pair_list:
            pairs.append((pair["master_id"], pair["file_type"]))
        if not pairs:
            return 0
        return (
            self.db.query(File).filter(tuple_(File.master_id, File.file_type).in_(pairs)).delete()
        )
