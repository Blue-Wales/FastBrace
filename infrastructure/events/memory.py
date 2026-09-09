#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : memory.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

import atexit
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

from loguru import logger

from infrastructure.events.base import (
    BaseEventBus,
    BaseEventHandler,
    BaseEventTask,
    DomainEvent,
)
from infrastructure.events.event_bus_service import EventBusService

DEFAULT_CONCURRENCY = 10


class MemoryEventTask(BaseEventTask):
    """内存事件任务"""

    def __init__(self, event_id: str, futures: dict[str, Future]):
        super().__init__(event_id)
        self._futures = futures

    def is_done(self) -> bool:
        """事件任务是否完成"""
        return all(future.done() for future in self._futures.values())

    def get_results(self) -> dict[str, Any]:
        """获取事件任务结果"""
        return {handler_type: future.result() for handler_type, future in self._futures.items()}

    def join(self, timeout: float | None = None) -> None:
        """等待事件任务完成"""
        for future in self._futures.values():
            future.result(timeout)


@EventBusService.register_bus("memory_event_bus")
class MemoryEventBus(BaseEventBus):
    """本地内存事件总线"""

    IS_LOCAL: bool = True

    def __init__(self):
        super().__init__()
        self._executor: ThreadPoolExecutor | None = None
        # 注册程序退出时的清理函数
        atexit.register(self._cleanup_executor)

    def _cleanup_executor(self):
        """清理线程池，避免资源泄漏"""
        if self._executor and not self._executor._shutdown:
            try:
                self._executor.shutdown(wait=False, cancel_futures=True)
                logger.debug("MemoryEventBus线程池已清理")
            except Exception:
                pass  # 程序退出时忽略清理错误

    def _start_impl(self, concurrency: int) -> None:
        """启动事件总线"""
        if self._executor is None:
            concurrency = concurrency if concurrency > 0 else DEFAULT_CONCURRENCY
            self._executor = ThreadPoolExecutor(
                max_workers=concurrency, thread_name_prefix="MemoryEventBus"
            )

    def _stop_impl(self) -> None:
        """停止事件总线"""
        if self._executor:
            self._executor.shutdown(wait=True, cancel_futures=True)
            self._executor = None

    def _subscribe_handler_impl(self, domain: str, handler: BaseEventHandler) -> None:
        """订阅事件处理器"""
    def publish_async(self, event: DomainEvent, scope: list[str] | None = None) -> MemoryEventTask:
        """发布事件(异步模式)"""
        if not self.is_started or self._executor is None:
            logger.error("内存事件总线未启动或执行器未初始化")
            return MemoryEventTask(event.event_id, {})

        results = {}
        for handler in self.get_all_handlers():
            if handler.can_handle(event.event_type):
                future = self._executor.submit(handler.handle, event)
                results[handler.__type__] = future

        return MemoryEventTask(event.event_id, results)

    def publish_sync(self, event: DomainEvent, scope: list[str] | None = None) -> dict[str, Any]:
        """发布事件(同步模式)"""
        result = self.publish_async(event, scope)
        result.join()
        return result.get_results()
