#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : base.py
@Author  : bright
@Date    : 2026-08-22
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Generator
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from infrastructure.utils.id_generator import SnowflakeIDGenerator
from infrastructure.utils.oop_utils import (
    ABCSingletonMeta,
    ClsAttrCheckMixin,
    NeedImplemented,
)


class DomainEvent(BaseModel):
    """领域事件基类"""

    aggregate_type: str
    event_type: str
    event_data: dict
    event_id: str = Field(default_factory=lambda: str(SnowflakeIDGenerator()()))
    aggregate_id: int | None = Field(default=None)
    occurred_at: datetime | None = Field(default_factory=datetime.now)
    version: int = 1
    # 事件为本地事件还是跨域事件
    # 本地事件：仅在当前领域内处理
    # 跨域事件：同时当前域和其他领域内处理
    is_local: bool = True


class EventScope(Enum):
    """事件范围"""

    LOCAL = "local"
    CROSS = "cross"
    ALL = "all"


class BaseEventHandler(ABC, ClsAttrCheckMixin):
    """事件处理器基类 - 使用模板方法模式确保can_handle检查"""

    __type__: str = NeedImplemented()
    SUPPORTED_EVENT_TYPES: list[str] = NeedImplemented()

    def can_handle(self, event_type: str) -> bool:
        """检查是否可以处理指定类型的事件

        :param event_type: 事件类型
        :return: 是否可以处理
        """
        return event_type in self.SUPPORTED_EVENT_TYPES

    def handle(self, event: DomainEvent) -> None:
        """处理事件 - 模板方法，确保先执行can_handle检查

        :param event: 领域事件
        """
        if not self.can_handle(event.event_type):
            logger.debug(f"处理器 {self.__class__.__name__} 不支持事件类型: {event.event_type}")
            return

        # 调用子类实现的具体处理逻辑
        self._handle_event(event)

    @abstractmethod
    def _handle_event(self, event: DomainEvent) -> None:
        """具体的事件处理逻辑 - 子类必须实现

        :param event: 领域事件
        """

class EventHandlerRegistry:
    """事件处理器注册表"""

    def __init__(self):
        self.handlers: dict[str, dict[str, BaseEventHandler]] = defaultdict(dict)

    def register_handler(
        self,
        domain: str,
        handler_type: str,
        handler: BaseEventHandler,
        is_local: bool = False,
    ) -> None:
        """注册事件处理器"""
        if domain not in self.handlers:
            self.handlers[domain] = {}

        self.handlers[domain][self.gen_handler_key(handler_type, is_local)] = handler

    @staticmethod
    def gen_handler_key(handler_type: str, is_local: bool) -> str:
        """生成事件处理器键"""
        if is_local:
            return f"{handler_type}.local"
        return f"{handler_type}.cross"

    def get_handler(self, domain: str, handler_type: str, is_local: bool) -> BaseEventHandler:
        """获取事件处理器"""
        return self.handlers[domain][self.gen_handler_key(handler_type, is_local)]

    def get_all_handlers(
        self, scope: EventScope | None = None
    ) -> Generator[BaseEventHandler, None, None]:
        """获取所有事件处理器"""
        for domain in self.handlers:
            for k, handler in self.handlers[domain].items():
                if scope and scope != EventScope.ALL and not k.endswith(f".{scope.value}"):
                    continue

                yield handler

    def has_handler(self, domain: str, handler_type: str, is_local: bool) -> bool:
        """判断是否存在事件处理器"""
        return self.gen_handler_key(handler_type, is_local) in self.handlers[domain]

    def statistics(self) -> dict[str, Any]:
        """统计事件处理器"""
        return {
            "total_domains": len(self.handlers),
            "total_events": sum(len(handlers) for handlers in self.handlers.values()),
        }


class BaseEventTask(ABC):
    """事件任务"""

    def __init__(self, event_id: str):
        self.event_id = event_id

    @abstractmethod
    def is_done(self) -> bool:
        """事件任务是否完成"""
    @abstractmethod
    def get_results(self) -> dict[str, Any]:
        """获取事件任务结果

        :return: 事件任务结果，key为事件处理器类型，value为事件处理结果
        """
    @abstractmethod
    def join(self, timeout: float | None = None) -> None:
        """等待事件任务完成"""

class BaseEventBus(metaclass=ABCSingletonMeta):
    """事件总线抽象基类 - 统一的事件发布订阅接口"""

    IS_LOCAL: bool = False

    def __init__(self):
        self._started = False
        self.handler_registry = EventHandlerRegistry()

    @property
    def is_started(self) -> bool:
        """事件总线是否已启动"""
        return self._started

    def start(self, concurrency: int = 0) -> None:
        """启动事件总线"""
        if self._started:
            logger.warning("事件总线已启动")
            return

        self._started = True
        self._start_impl(concurrency)

    def stop(self) -> None:
        """停止事件总线"""
        if not self._started:
            logger.warning("事件总线未启动")
            return

        self._started = False
        self._stop_impl()

    @abstractmethod
    def _start_impl(self, concurrency: int) -> None:
        """启动事件总线"""
    @abstractmethod
    def _stop_impl(self) -> None:
        """停止事件总线"""
    def subscribe(self, domain: str, handler: BaseEventHandler) -> None:
        """订阅事件处理器"""
        if self.handler_registry.has_handler(domain, handler.__type__, self.IS_LOCAL):
            logger.debug(f"事件处理器 {domain}:{handler.__type__} 已注册")
            return

        self.handler_registry.register_handler(domain, handler.__type__, handler, self.IS_LOCAL)
        self._subscribe_handler_impl(domain, handler)
        logger.info(f"事件处理器 {domain}:{handler.__type__} 注册成功")

    def get_handler(self, domain: str, handler_type: str) -> BaseEventHandler:
        """获取事件处理器"""
        return self.handler_registry.get_handler(domain, handler_type, self.IS_LOCAL)

    def get_all_handlers(
        self, scope: EventScope | None = None
    ) -> Generator[BaseEventHandler, None, None]:
        """获取所有事件处理器"""
        return self.handler_registry.get_all_handlers(scope)

    @abstractmethod
    def publish_async(self, event: DomainEvent, scope: list[str] | None = None) -> BaseEventTask:
        """
        发布事件(异步模式)
        :return: 事件任务
        """
    @abstractmethod
    def publish_sync(self, event: DomainEvent, scope: list[str] | None = None) -> dict[str, Any]:
        """发布事件(同步模式)
        """
    @abstractmethod
    def _subscribe_handler_impl(self, domain: str, handler: BaseEventHandler) -> None:
        """订阅事件处理器的具体实现"""
