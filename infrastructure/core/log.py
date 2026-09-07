#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : log.py
@Author  : bright
@Date    : 2026-08-22
"""

import atexit
import contextlib
import os
import signal
import sys
import threading
import time
import weakref
from enum import Enum

from loguru import logger
from pydantic import BaseModel, Field

from infrastructure.core.settings import app_settings
from infrastructure.utils.oop_utils import SingletonMeta


class ModulesForLogger(Enum):
    """模块名"""

    API = "api_log"
    EVENT_BUS = "event_log"
    CRON_JOB = "cron_log"


class LoggerParams(BaseModel):
    """日志参数"""

    env: str | None = Field(title="环境类型", default=None)
    log_dir: str = Field(title="日志目录")
    log_name: str = Field(title="日志文件名")
    debug: bool = Field(title="是否开启debug日志", default=False)
    log_rotation: str = Field(title="主日志轮转大小")
    log_retention: int = Field(title="主日志保留数量")
    error_log_rotation: str = Field(title="错误日志轮转大小")
    error_log_retention: int = Field(title="错误日志保留数量")
    use_async_logging: bool = Field(title="是否使用异步日志队列", default=True)


class LoggerManager(metaclass=SingletonMeta):
    """日志管理器"""

    def __init__(self):
        self.log_params: LoggerParams | None = None
        self._current_debug_enabled = False
        self._handler_ids: dict[str, int] = {}
        self._cleanup_registered = False
        self._shutdown_event = threading.Event()
        self._signal_handlers_registered = False

    @property
    def log_level(self):
        return "DEBUG" if self._current_debug_enabled else "INFO"

    def init_logger(self, log_params: LoggerParams):
        """初始化日志"""
        self.log_params = log_params

        # 开发环境默认开启debug，初始化时指定debug为True，则强制开启debug
        self._current_debug_enabled = self.log_params.env == "dev" or self.log_params.debug

        os.makedirs(self.log_params.log_dir, exist_ok=True)

        # 移除默认Handler
        logger.remove()

        # 添加日志处理器
        self._add_log_handlers()

        # 注册清理机制
        self._register_cleanup_mechanisms()

        # 注册信号处理（只在Unix系统下注册）
        if hasattr(signal, "SIGUSR1") and not self._signal_handlers_registered:
            signal.signal(signal.SIGUSR1, self._handle_log_level_signal)
            signal.signal(signal.SIGUSR2, self._handle_log_info_signal)
            self._signal_handlers_registered = True
            logger.info(
                f"日志信号处理已注册: kill -USR1 {os.getpid()} (切换debug), "
                f"kill -USR2 {os.getpid()} (查看状态)"
            )

        logger.debug("日志管理器初始化完成")

    def _register_cleanup_mechanisms(self):
        """注册多种清理机制，确保资源能够被正确释放"""
        if self._cleanup_registered:
            return

        self._cleanup_registered = True

        # 1. atexit 回调 - 正常退出时调用
        atexit.register(self._cleanup_handlers)

        # 2. 注册信号处理器 - 处理进程终止信号
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self._signal_cleanup_handler)
        if hasattr(signal, "SIGINT"):  # Ctrl+C
            signal.signal(signal.SIGINT, self._signal_cleanup_handler)

        # 3. 使用弱引用清理器 - 当对象被垃圾回收时调用
        weakref.finalize(self, self._force_cleanup, self._handler_ids.copy())

    def _signal_cleanup_handler(self, signum, frame):
        """信号处理器：清理日志资源后重新发送信号"""
        logger.debug(f"收到终止信号 {signum}，开始清理日志资源...")
        self._cleanup_handlers()

        signal.signal(signum, signal.SIG_DFL)
        # 重新发送信号，确保程序正常退出
        if signum == signal.SIGTERM:
            os.kill(os.getpid(), signal.SIGTERM)
        elif signum == signal.SIGINT:
            os.kill(os.getpid(), signal.SIGINT)

    @staticmethod
    def _force_cleanup(handler_ids_copy):
        """强制清理函数 - 由弱引用清理器调用"""
        with contextlib.suppress(BaseException):
            for handler_id in handler_ids_copy.values():
                logger.remove(handler_id)
            logger.complete()

    def _should_use_async_logging(self) -> bool:
        """判断是否应该使用异步日志"""
        # 确保 log_params 已初始化
        if self.log_params is None:
            return False

        # 1. 显式配置
        if hasattr(self.log_params, "use_async_logging"):
            return self.log_params.use_async_logging

        # 2. 环境变量控制
        env_async = os.environ.get("LOG_ASYNC", "").lower()
        if env_async in ("true", "1", "yes"):
            return True
        if env_async in ("false", "0", "no"):
            return False

        # 3. 默认策略：生产环境且非调试模式时使用异步
        # 开发环境或调试模式下为了避免资源泄漏，使用同步日志
        return (
            self.log_params.env == "prod"
            and not self._current_debug_enabled
            and not os.environ.get("PYTEST_CURRENT_TEST")  # 测试环境下不使用异步
        )

    def _cleanup_handlers(self):
        """清理日志处理器，避免资源泄漏"""
        if self._shutdown_event.is_set():
            return  # 避免重复清理

        self._shutdown_event.set()

        try:
            logger.debug("开始清理日志处理器...")

            # 1. 先停止接受新的日志
            logger.stop()

            # 2. 等待现有日志处理完成
            logger.complete()

            # 3. 移除所有自定义的handler
            for handler_name, handler_id in list(self._handler_ids.items()):
                try:
                    logger.remove(handler_id)
                    logger.debug(f"已移除日志处理器: {handler_name}")
                except (ValueError, KeyError):
                    pass  # handler可能已经被移除

            self._handler_ids.clear()

            # 4. 短暂等待，确保后台进程完全关闭
            time.sleep(0.1)

        except Exception as e:
            # 程序退出时的错误不影响正常退出
            print(f"日志清理警告: {e}", file=sys.stderr)

    def __init_check(func):
        """初始化检查"""
        def decorator(*args, **kwargs):
            if args[0].log_params is None:
                logger.warning("尚未初始化日志，请先调用init_logger方法")
                return None

            return func(*args, **kwargs)

        return decorator

    def _add_log_handlers(self):
        """添加日志处理器"""
        # 添加默认request_id的过滤器
        def add_request_id(record):
            if "request_id" not in record["extra"]:
                record["extra"]["request_id"] = "system"
            return record

        # 决定是否使用异步队列
        use_enqueue = self._should_use_async_logging()

        if use_enqueue:
            logger.info("使用异步日志队列模式")
        else:
            logger.info("使用同步日志模式")

        # 主日志文件 - 记录所有级别的日志（JSON 结构化输出，纯按大小轮转）
        # serialize=True：每条日志输出为单行 JSON，异常堆栈中的换行会被转义，
        # 便于日志采集工具按字段解析，无需多行/正则处理
        main_handler_id = logger.add(
            os.path.join(self.log_params.log_dir, f"{self.log_params.log_name}.log"),
            rotation=self.log_params.log_rotation,  # 单文件最大200MB
            retention=self.log_params.log_retention,  # 最多保留5个轮转文件
            enqueue=use_enqueue,  # 根据环境和配置决定是否使用异步队列
            level=self.log_level,
            serialize=True,  # JSON 输出，便于结构化采集与检索
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | "
                "{extra[request_id]} | {name}:{function}:{line} | {message}"
            ),
            compression="tar.gz",  # 压缩旧文件
            filter=add_request_id,
        )
        self._handler_ids["main"] = main_handler_id

        # 错误日志文件 - 单独记录WARNING及以上级别（JSON 结构化输出，纯按大小轮转）
        error_handler_id = logger.add(
            os.path.join(self.log_params.log_dir, f"{self.log_params.log_name}_error.log"),
            rotation=self.log_params.error_log_rotation,  # 错误日志文件相对较小
            retention=self.log_params.error_log_retention,  # 最多保留3个轮转文件
            enqueue=use_enqueue,  # 根据环境和配置决定是否使用异步队列
            level="WARNING",  # 只记录WARNING/ERROR/CRITICAL
            serialize=True,  # JSON 输出，便于结构化采集与检索
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | "
                "{extra[request_id]} | {name}:{function}:{line} | {message}"
            ),
            compression="tar.gz",
            filter=add_request_id,
        )
        self._handler_ids["error"] = error_handler_id

        # 控制台输出 - 所有环境均输出到 stderr，便于 docker logs / 日志采集器直接采集
        console_handler_id = logger.add(
            sys.stderr,
            level=self.log_level,
            format=(
                "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | "
                "{extra[request_id]} | {name}:{function}:{line} | {message}"
            ),
            colorize=False,  # 非 TTY 环境禁用颜色，避免 docker logs 出现转义码
            enqueue=False,  # 控制台输出始终使用同步模式
            filter=add_request_id,
        )
        self._handler_ids["console"] = console_handler_id

    @__init_check
    def toggle_debug(self):
        """切换debug日志状态"""
        # 切换状态
        self._current_debug_enabled = not self._current_debug_enabled
        return self._refresh_log_handlers()

    @__init_check
    def turn_off_debug(self):
        """关闭debug日志"""
        self._current_debug_enabled = False
        return self._refresh_log_handlers()

    @__init_check
    def turn_on_debug(self):
        """开启debug日志"""
        self._current_debug_enabled = True
        return self._refresh_log_handlers()

    def _refresh_log_handlers(self):
        """刷新日志处理器"""
        # 移除现有的handler
        for handler_id in self._handler_ids.values():
            with contextlib.suppress(ValueError):
                logger.remove(handler_id)

        # 清空handler记录
        self._handler_ids.clear()

        # 重新添加handler
        self._add_log_handlers()

        status = "已开启" if self._current_debug_enabled else "已关闭"
        logger.info(f"日志debug模式{status} (PID: {os.getpid()})")

        return self._current_debug_enabled

    @__init_check
    def get_log_status(self):
        """获取当前日志状态"""
        return {
            "debug_enabled": self._current_debug_enabled,
            "log_level": self.log_level,
            "environment": self.log_params.env,
            "log_directory": self.log_params.log_dir,
            "process_id": os.getpid(),
            "handlers_count": len(self._handler_ids),
            "async_logging": self._should_use_async_logging(),
        }

    def _handle_log_level_signal(self, signum, frame):
        """处理日志等级切换信号 (SIGUSR1)"""
        if signum == signal.SIGUSR1:
            logger.info("收到信号 SIGUSR1，正在切换日志debug模式...")
            new_status = self.toggle_debug()
            # 注意：不再向子进程发送信号，避免在多进程环境下的问题
            logger.info(f"日志debug模式已{'开启' if new_status else '关闭'}")
        else:
            logger.info(f"收到未知信号: {signum}")

    def _handle_log_info_signal(self, signum, frame):
        """处理日志状态查询信号 (SIGUSR2)"""
        if signum == signal.SIGUSR2:
            status = self.get_log_status()
            logger.info(f"当前日志状态: {status}")
        else:
            logger.info(f"收到未知信号: {signum}")

    def force_cleanup(self):
        """手动强制清理（用于测试或特殊情况）"""
        logger.info("手动触发日志清理...")
        self._cleanup_handlers()


logger_manager = LoggerManager()


def init_logger(module_name: ModulesForLogger) -> LoggerManager:
    """初始化日志"""
    log_settings = getattr(app_settings, module_name.value)
    logger_manager.init_logger(
        LoggerParams(
            env=app_settings.env,
            log_dir=log_settings.log_dir,
            log_name=log_settings.log_name,
            debug=log_settings.debug,
            log_rotation=log_settings.log_rotation,
            log_retention=log_settings.log_retention,
            error_log_rotation=log_settings.error_log_rotation,
            error_log_retention=log_settings.error_log_retention,
            use_async_logging=log_settings.use_async_logging,
        )
    )

    if os.environ.get("LOG_DEBUG", "").lower() in ("true", "1", "yes"):
        logger_manager.turn_on_debug()
        logger.debug("通过环境变量LOG_DEBUG强制开启debug日志")

    return logger_manager
