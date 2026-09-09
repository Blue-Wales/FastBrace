#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : id_generator.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

import random
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime


class IdGenerator(ABC):
    """ID生成策略接口"""

    @abstractmethod
    def __call__(self) -> str:
        """生成唯一ID"""
        pass

    @property
    @abstractmethod
    def id_type(self):
        """返回id数据类型"""
        pass


class SnowflakeIDGenerator(IdGenerator):
    _instance = None
    _lock = threading.Lock()

    # 雪花算法参数配置 - 生成8-10位数字ID，8-10位数字范围: 10,000,000 ~ 9,999,999,999
    # 使用相对时间戳(从当天开始) + 序列号 + 随机数的方式
    _EPOCH = None  # 每天重置纪元时间
    _WORKER_ID_BITS = 2  # 机器ID位数2位(0-3)
    _DATACENTER_ID_BITS = 2  # 数据中心ID位数2位(0-3)
    _SEQUENCE_BITS = 8  # 序列号位数8位(0-255)

    def __new__(cls, worker_id=0, datacenter_id=0):
        """单例模式实现"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    # 校验ID范围
                    max_worker = (1 << cls._WORKER_ID_BITS) - 1
                    max_dc = (1 << cls._DATACENTER_ID_BITS) - 1
                    if worker_id > max_worker or worker_id < 0:
                        raise ValueError(f"Worker ID必须在0~{max_worker}之间")
                    if datacenter_id > max_dc or datacenter_id < 0:
                        raise ValueError(f"Datacenter ID必须在0~{max_dc}之间")

                    cls._instance = super().__new__(cls)
                    cls._instance.worker_id = worker_id
                    cls._instance.datacenter_id = datacenter_id
                    cls._instance.sequence = 0
                    cls._instance.last_timestamp = -1
                    # 位移计算
                    cls._instance._timestamp_shift = (
                        cls._SEQUENCE_BITS + cls._WORKER_ID_BITS + cls._DATACENTER_ID_BITS
                    )
                    cls._instance._datacenter_shift = cls._SEQUENCE_BITS + cls._WORKER_ID_BITS
                    cls._instance._worker_shift = cls._SEQUENCE_BITS
                    cls._instance._sequence_mask = (1 << cls._SEQUENCE_BITS) - 1
        return cls._instance

    def _get_daily_epoch(self):
        """获取当天0点的时间戳"""
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return int(today.timestamp())

    def _current_time(self):
        """获取当前秒级时间戳"""
        return int(time.time())

    def _wait_next_second(self, last_timestamp):
        """等待到下一秒"""
        timestamp = self._current_time()
        while timestamp <= last_timestamp:
            time.sleep(0.01)
            timestamp = self._current_time()
        return timestamp

    def __call__(self):
        """生成全局唯一ID (8-10位数字)"""
        with self._lock:  # 线程安全锁
            timestamp = self._current_time()
            daily_epoch = self._get_daily_epoch()

            # 时钟回拨检测
            if timestamp < self.last_timestamp:
                raise ValueError(
                    f"时钟回拨异常，拒绝生成ID。回拨时间：{self.last_timestamp - timestamp}s"
                )

            # 同一秒内序列递增
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self._sequence_mask
                if self.sequence == 0:  # 当前秒序列号耗尽
                    timestamp = self._wait_next_second(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            # 计算当天经过的秒数 (0-86399，需要17位二进制)
            seconds_of_day = timestamp - daily_epoch

            # 组合生成ID
            # 当天秒数(17位) + 数据中心(2位) + 机器ID(2位) + 序列号(8位) = 29位
            # 最大值为 2^29 - 1 = 536,870,911 (9位数字)
            return (
                (seconds_of_day << self._timestamp_shift)
                | (self.datacenter_id << self._datacenter_shift)
                | (self.worker_id << self._worker_shift)
                | self.sequence
            )

    @property
    def id_type(self):
        return int


class FileIDGenerator(IdGenerator):
    def __call__(self):
        """
        随机生成文件名称
        :return:
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{timestamp}_{random.randint(100, 999)}"

    @property
    def id_type(self):
        return str


# 使用示例
if __name__ == "__main__":
    pass
