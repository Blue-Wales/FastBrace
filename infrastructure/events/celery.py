#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : celery.py
@Author  : bright
@Date    : 2026-08-22
"""

import platform
import traceback
from typing import Any

from celery import Celery
from celery.result import AsyncResult
from loguru import logger

from infrastructure.core.log import logger_manager
from infrastructure.core.settings import app_settings
from infrastructure.events.base import (
    BaseEventBus,
    BaseEventHandler,
    BaseEventTask,
    DomainEvent,
    EventScope,
)
from infrastructure.events.event_bus_service import EventBusService


class CeleryEventTask(BaseEventTask):
    """Celery事件任务"""

    def __init__(self, event_id: str, task_results: dict[str, AsyncResult]):
        super().__init__(event_id)
        self._task_results = task_results

    def is_done(self) -> bool:
        """事件任务是否完成"""
        return all(task_result.ready() for task_result in self._task_results.values())

    def get_results(self) -> dict[str, Any]:
        """获取事件任务结果"""
        results = {}
        for handler_type, task_result in self._task_results.items():
            results[handler_type] = task_result.result
        return results

    def join(self, timeout: float | None = None) -> None:
        """等待事件任务完成"""
        for task_result in self._task_results.values():
            task_result.get(timeout=timeout)


@EventBusService.register_bus("celery_event_bus")
class CeleryEventBus(BaseEventBus):
    """基于Celery的事件总线实现"""

    IS_LOCAL: bool = False

    def __init__(self):
        super().__init__()

        self.celery_config = app_settings.celery
        logger.debug(
            f"celery配置，broker: {self.celery_config.broker_url}, "
            f"backend: {self.celery_config.result_backend}"
        )
        self.app = Celery(
            "event_bus",
            broker=self.celery_config.broker_url,
            backend=self.celery_config.result_backend,
        )

        # 配置Celery
        self.app.conf.update(
            result_expires=self.celery_config.result_expires,
            task_serializer=self.celery_config.task_serializer,
            accept_content=self.celery_config.accept_content,
            result_serializer=self.celery_config.result_serializer,
            enable_utc=self.celery_config.enable_utc,
            timezone=self.celery_config.timezone,
            task_track_started=self.celery_config.task_track_started,
            task_publish_retry=self.celery_config.task_publish_retry,
            task_acks_late=True,
            worker_prefetch_multiplier=1,
            task_create_missing_queues=True,
            task_reject_on_worker_lost=True,
            task_publish_retry_policy={
                "max_retries": self.celery_config.task_publish_retry_policy["max_retries"],
                "interval_start": self.celery_config.task_publish_retry_policy["interval_start"],
                "interval_step": self.celery_config.task_publish_retry_policy["interval_step"],
                "interval_max": self.celery_config.task_publish_retry_policy["interval_max"],
            },
        )
        # 为Windows系统添加特殊配置
        if platform.system() == "Windows":
            self.app.conf.update(worker_pool="solo")

    def _register_task(self, handler: BaseEventHandler) -> None:
        """注册Celery任务"""
        @self.app.task(name=handler.__type__, bind=True)
        def handle_event(task_self, event_data: dict[str, Any]) -> bool:
            """处理事件的Celery任务

            celery任务不负责异常处理，若任务失败则仅打印日志，请handler内部处理异常或重试机制
            """
            try:
                # 创建事件对象
                event = DomainEvent.model_validate(event_data)
                logger.debug(f"开始处理事件: {event}")
                handler.handle(event)
                logger.info(
                    f"事件{event.event_type}处理成功: {handler.__type__} -> {handler.__class__.__name__}"
                )
                if task_self.request.delivery_info.get("routing_key"):
                    logger.debug(f"准备ACK任务: {task_self.request.id}")
            except Exception as e:
                logger.error(
                    f"事件{event.event_type}处理失败: {handler.__type__} -> {handler.__class__.__name__}: {e}, "
                    f"traceback: {traceback.format_exc()}"
                )
            return True

    def _register_all_tasks(self):
        for handler in self.get_all_handlers(scope=EventScope.CROSS):
            logger.debug(f"register task: {handler.__type__}: {handler.__class__.__name__}")
            self._register_task(handler)

    def _start_worker(self, concurrency: int) -> None:
        """启动Celery Worker"""
        try:
            self._register_all_tasks()
            # 启动Celery Worker]
            celery_log_level = "DEBUG" if logger_manager.log_level == "DEBUG" else "INFO"
            logger.info(
                f"启动Celery Worker: {self.app.worker_main}, "
                f"并发数: {concurrency if concurrency > 0 else '默认'}"
            )
            args = [
                "worker",
                f"--loglevel={celery_log_level}",
                "--without-gossip",
                "--without-mingle",
                "--without-heartbeat",
            ]
            if concurrency > 0:
                args.append(f"--concurrency={concurrency}")
            self.app.worker_main(args)
        except Exception as e:
            logger.error(f"Celery事件总线启动失败: {e}, traceback: {traceback.format_exc()}")
            raise

    def _start_impl(self, concurrency: int) -> None:
        """启动事件总线"""
        self._start_worker(concurrency)

    def _stop_impl(self) -> None:
        """停止事件总线"""
        try:
            # 停止Celery Worker
            self.app.control.shutdown()
            logger.info("Celery事件总线已停止")
        except Exception as e:
            logger.error(f"Celery事件总线停止失败: {e}, traceback: {traceback.format_exc()}")

    def _subscribe_handler_impl(self, domain: str, handler: BaseEventHandler) -> None:
        """订阅事件处理器"""
        pass

    # TODO 可以加入回调函数传递
    def publish_async(self, event: DomainEvent, scope: list[str] | None = None) -> CeleryEventTask:
        """发布事件(异步模式)"""
        results = {}
        try:
            # 序列化事件
            event_data = event.model_dump()
            for handler in self.get_all_handlers(scope=EventScope.CROSS):
                logger.debug(f"send task: {handler.__type__}")
                if event.event_type in handler.SUPPORTED_EVENT_TYPES:
                    task_result = self.app.send_task(handler.__type__, [event_data])
                    results[handler.__type__] = task_result

            logger.info(f"已发布事件: {event.event_type} - {event.aggregate_id}")

        except Exception as e:
            logger.error(f"发布事件失败: {e}, traceback: {traceback.format_exc()}")
            raise

        return CeleryEventTask(event.event_id, results)

    def publish_sync(self, event: DomainEvent, scope: list[str] | None = None) -> dict[str, Any]:
        """发布事件(同步模式)"""
        result = self.publish_async(event, scope)
        result.join()
        return result.get_results()
