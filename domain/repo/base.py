#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : base.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 基础仓储实现
"""

from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session


class BaseRepository:
    """基础仓库实现"""

    def __init__(self, db: Session | None = None):
        self.db = db

    def _to_entity(self, orm_obj, entity):
        """通过 Pydantic 属性模式将查询结果转换为领域对象。"""
        return entity.model_validate(orm_obj)

    def _to_model(self, model, entity):
        """按 ORM 表字段裁剪实体数据并构造模型。"""
        parameters = {c.name for c in model.__table__.columns}
        return model(**entity.model_dump(include=parameters, exclude_none=True))

    def batch_upsert(self, model, data_list: list[dict], on_duplicate_key_list: list[str]):
        """使用 MySQL ON DUPLICATE KEY 批量 upsert。"""
        stmt = insert(model).values(data_list)
        on_duplicate_key_dict = {key: getattr(stmt.inserted, key) for key in on_duplicate_key_list}
        do_update_stmt = stmt.on_duplicate_key_update(**on_duplicate_key_dict)
        result = self.db.execute(do_update_stmt)
        return result.rowcount

    def flush(self) -> None:
        """将当前会话中挂起的变更同步到数据库，但不提交事务。"""
        self.db.flush()
