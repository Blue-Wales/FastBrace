#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : file.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 文件仓储接口
"""

from typing import Protocol

from domain.repo.interfaces.base import IBaseRepository
from domain.value_object.file_vo import FileVO


class IFileRepository(IBaseRepository, Protocol):
    """统一文件资源关联的持久化契约。

    文件通过 `master_id + file_type` 关联业务实体。仓储只维护数据库关联，
    不上传或删除对象存储中的实体文件。
    """

    async def save(self, file_vo_list: list[dict]) -> None:
        """批量保存已转换为持久化映射的文件关联。

        Args:
            file_vo_list: 可直接写入文件模型的字段映射列表。

        Notes:
            调用方应先为每个资源填充 `master_id` 和 `file_type`。
        """
        ...

    async def get(self, master_id: int, file_types: list[int] | None = None) -> list[FileVO]:
        """查询单个业务实体关联的文件。

        Args:
            master_id: 业务实体 ID。
            file_types: 可选的文件类型过滤列表。

        Returns:
            匹配的文件值对象列表。
        """
        ...

    async def get_multiple(
        self, master_ids: list[int], file_types: list[int] | None = None
    ) -> list[FileVO]:
        """批量查询多个业务实体关联的文件。

        Args:
            master_ids: 业务实体 ID 列表。
            file_types: 可选的文件类型过滤列表。

        Returns:
            所有匹配的文件值对象，调用方可按 `master_id` 分组。
        """
        ...

    async def delete(self, pair_list: list[dict]) -> int:
        """批量删除指定业务实体和文件类型的关联。

        Args:
            pair_list: 包含 `master_id` 和 `file_type` 的映射列表。

        Returns:
            被删除的数据库记录数；列表为空时返回 `0`。

        Notes:
            该操作不删除对象存储文件。
        """
        ...
