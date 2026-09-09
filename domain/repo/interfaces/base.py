#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : base.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 基础仓储接口
"""

from typing import Protocol


class IBaseRepository(Protocol):
    """所有仓储可复用的基础持久化契约。

    业务仓储可继承该 Protocol 以获得通用批量写入能力。具体数据库方言、
    事务提交和异常转换由实现层负责。
    """

    def batch_upsert(self, model, data_list: list[dict], on_duplicate_key_list: list[str]) -> int:
        """批量插入数据，冲突时更新指定字段。

        Args:
            model: 目标持久化模型类。
            data_list: 待写入的字段映射列表。空列表的处理由具体实现约定。
            on_duplicate_key_list: 唯一键冲突时需要使用新值更新的字段名列表。

        Returns:
            数据库报告的受影响行数。

        Raises:
            SQLAlchemyError: 底层数据库执行失败且实现层未转换异常时抛出。

        Notes:
            该方法只执行写入，不负责提交事务。
        """
        ...

    def flush(self) -> None:
        """将当前会话中挂起的变更同步到数据库，但不提交事务。"""
        ...
