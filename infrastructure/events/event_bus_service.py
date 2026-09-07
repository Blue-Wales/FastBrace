#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : event_bus_service.py
@Author  : bright
@Date    : 2026-08-22
"""

import traceback
from collections import defaultdict
from typing import Any, ClassVar

from loguru import logger

from infrastructure.core.settings import EventBusSettings, app_settings
from infrastructure.events.base import (
    BaseEventBus,
    BaseEventHandler,
    BaseEventTask,
    DomainEvent,
)
from infrastructure.utils.oop_utils import SingletonMeta


class EventTaskChain(BaseEventTask):
    """事件任务链"""

    def __init__(self, event_id: str, tasks: list[BaseEventTask]):
        super().__init__(event_id)
        self.tasks = tasks

    def is_done(self) -> bool:
        return all(task.is_done() for task in self.tasks)

    def get_results(self) -> dict[str, Any]:
        results = {}
        for task in self.tasks:
            results.update(task.get_results())
        return results

    def join(self, timeout: float | None = None) -> None:
        for task in self.tasks:
            task.join(timeout)


class EventBusService(metaclass=SingletonMeta):
    """事件总线服务

    该类用于管理事件总线，包括启动、停止、发布事件等操作
    根据配置选择事件总线类型，目前支持celery和rabbitmq
    支持跨域事件和本地事件混合启动
    """

    _local_event_handlers_cls_cache: ClassVar[dict[str, list[type[BaseEventHandler]]]] = (
        defaultdict(list)
    )
    _cross_event_handlers_cls_cache: ClassVar[dict[str, list[type[BaseEventHandler]]]] = (
        defaultdict(list)
    )
    _event_bus_registry: ClassVar[dict[str, type[BaseEventBus]]] = {}

    def __init__(self, event_bus_settings: EventBusSettings):
        self.event_bus_settings = event_bus_settings
        self.cross_event_bus: BaseEventBus | None = None
        self.local_event_bus: BaseEventBus | None = None
        self.is_initialized = False

        self._initialize_event_buses()
        self._do_subscribe()

    def _initialize_event_buses(self):
        """延迟初始化事件总线"""
        if self.is_initialized:
            logger.debug("事件总线已初始化，跳过初始化")
            return

        self.cross_event_bus = self._get_event_bus(
            self.event_bus_settings.cross_domain_transport_type
        )
        self.local_event_bus = self._get_event_bus(self.event_bus_settings.local_transport_type)
        self.is_initialized = True

        logger.info(
            f"事件总线初始化完成: local={self.local_event_bus.__class__.__name__}, "
            f"cross={self.cross_event_bus.__class__.__name__}"
        )

    @classmethod
    def get_instance(cls) -> "EventBusService":
        """获取事件总线服务实例"""
        return cls(app_settings.event_bus)

    @classmethod
    def _get_event_bus(cls, transport_type: str) -> BaseEventBus | None:
        """获取事件总线实例

        :param transport_type: 事件总线类型
        :type transport_type: str
        :raises ValueError: 事件总线类型不是 BaseEventBus 的子类
        :return: 事件总线实例
        :rtype: BaseEventBus
        """
        event_bus_type = f"{transport_type}_event_bus"
        event_bus_cls = cls._event_bus_registry.get(event_bus_type)
        if not event_bus_cls:
            return None

        return event_bus_cls()

    @classmethod
    def register_bus(cls, event_bus_type: str):
        """注册事件总线"""
        def decorator(event_bus_class: type[BaseEventBus]):
            if not issubclass(event_bus_class, BaseEventBus):
                raise ValueError(f"事件总线{event_bus_class}必须继承自BaseEventBus")

            cls._event_bus_registry[event_bus_type] = event_bus_class
            return event_bus_class

        return decorator

    @classmethod
    def subscribe(cls, domain: str, is_local: bool = False):
        """订阅事件处理器（装饰器）"""
        def decorator(handler_class: type[BaseEventHandler]):
            if not issubclass(handler_class, BaseEventHandler):
                raise ValueError(f"事件处理器{handler_class}必须继承自BaseEventHandler")

            if is_local:
                cls._local_event_handlers_cls_cache[domain].append(handler_class)
            else:
                cls._cross_event_handlers_cls_cache[domain].append(handler_class)

            return handler_class

        return decorator

    def publish_async(self, event: DomainEvent) -> BaseEventTask:
        """发布事件（异步模式）"""
        tasks = []
        if self.local_event_bus:
            try:
                local_task = self.local_event_bus.publish_async(event)
                tasks.append(local_task)
            except Exception as e:
                logger.error(
                    f"发布本地事件失败，事件类型: {event.event_type}, "
                    f"事件ID: {event.event_id}, "
                    f"错误信息: {e}, "
                    f"堆栈信息: {traceback.format_exc()}"
                )

        if not event.is_local and self.cross_event_bus:
            # 对于非本地事件，还要同步发送跨域事件
            try:
                cross_task = self.cross_event_bus.publish_async(event)
                tasks.append(cross_task)
            except Exception as e:
                logger.error(
                    f"发布跨域事件失败，事件类型: {event.event_type}, "
                    f"事件ID: {event.event_id}, "
                    f"错误信息: {e}, "
                    f"堆栈信息: {traceback.format_exc()}"
                )

        return EventTaskChain(event.event_id, tasks)

    def publish_sync(self, event: DomainEvent) -> dict[str, Any]:
        """发布事件（同步模式）"""
        task = self.publish_async(event)
        task.join()
        return task.get_results()

    def _do_local_subscribe(self):
        """订阅本地事件处理器"""
        if not self.local_event_bus:
            logger.debug("本地事件总线未初始化，跳过订阅")
            return

        logger.info(f"执行本地事件处理器订阅，总计：{len(self._local_event_handlers_cls_cache)}")
        for domain, handler_cls_list in self._local_event_handlers_cls_cache.items():
            for handler_cls in handler_cls_list:
                self.local_event_bus.subscribe(domain, handler_cls())

        logger.info("执行本地事件处理器订阅完成，清空缓存")
        self._local_event_handlers_cls_cache.clear()

    def _do_cross_subscribe(self):
        """订阅跨域事件处理器"""
        if not self.cross_event_bus:
            logger.debug("跨域事件总线未初始化，跳过订阅")
            return

        logger.info(f"执行跨域事件处理器订阅，总计：{len(self._cross_event_handlers_cls_cache)}")
        for domain, handler_cls_list in self._cross_event_handlers_cls_cache.items():
            for handler_cls in handler_cls_list:
                self.cross_event_bus.subscribe(domain, handler_cls())

        logger.info("执行跨域事件处理器订阅完成，清空缓存")
        self._cross_event_handlers_cls_cache.clear()

    def _do_subscribe(self):
        """订阅事件处理器"""
        self._do_local_subscribe()
        self._do_cross_subscribe()

    def start_local(self):
        """启动本地事件总线"""
        if not self.local_event_bus:
            logger.warning("本地事件总线未初始化，跳过启动")
            return

        concurrency = self.event_bus_settings.local_event_bus_concurrency
        logger.info(
            f"启动本地事件总线<{self.local_event_bus.__class__.__name__}>，"
            f"并发数: {concurrency if concurrency > 0 else '默认'}"
        )
        self.local_event_bus.start(concurrency)

    def start_cross(self):
        """启动跨域事件总线"""
        if not self.cross_event_bus:
            logger.warning("跨域事件总线未初始化，跳过启动")
            return

        concurrency = self.event_bus_settings.cross_domain_event_bus_concurrency
        logger.info(
            f"启动跨域事件总线<{self.cross_event_bus.__class__.__name__}>，"
            f"并发数: {concurrency if concurrency > 0 else '默认'}"
        )
        self.cross_event_bus.start(concurrency)

    def stop_local(self):
        """停止本地事件总线"""
        if not self.local_event_bus:
            logger.debug("本地事件总线未初始化，跳过停止")
            return

        self.local_event_bus.stop()
        logger.info("本地事件总线停止完成")

    def stop_cross(self):
        """停止跨域事件总线"""
        if not self.cross_event_bus:
            logger.debug("跨域事件总线未初始化，跳过停止")
            return

        self.cross_event_bus.stop()
        logger.info("跨域事件总线停止完成")

    def stop_all(self):
        """停止所有事件总线"""
        self.stop_local()
        self.stop_cross()
