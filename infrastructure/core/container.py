#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : container.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : IoC 容器
"""

import threading
from typing import Any

from infrastructure.core.enum_var import BeanScope
from infrastructure.core.error_handler import GlobalException


class BeanDefinition:
    """已注册 Bean 的元数据。"""

    def __init__(self, bean_class: type, scope: str = BeanScope.SINGLETON.value):
        self.bean_class = bean_class
        self.scope = scope


class Container:
    """依赖注入容器。

    支持：
    - 单例作用域：跨请求共享同一个实例
    - 多例作用域：每次获取都创建新实例
    """

    def __init__(self):
        self._bean_definitions: dict[str, BeanDefinition] = {}
        self._singleton_instances: dict[str, Any] = {}
        self._lock = threading.Lock()

    def register(self, name: str, bean_class: type, scope: str = BeanScope.PROTOTYPE.value):
        """注册 Bean 定义。"""
        if name in self._bean_definitions:
            raise GlobalException(f"Bean '{name}' 已注册")
        self._bean_definitions[name] = BeanDefinition(bean_class, scope)

    def injectable(self, name: str, scope: str = BeanScope.SINGLETON.value):
        """用于自动注册 Bean 的装饰器。"""
        def decorator(cls: type):
            self.register(name, cls, scope)
            return cls

        return decorator

    def autowire(self, name: str, scope: str = BeanScope.SINGLETON.value):
        """兼容历史装饰器名称的别名。"""
        return self.injectable(name=name, scope=scope)

    def get_bean(self, name: str, **kwargs) -> Any:
        """获取 Bean 实例。"""
        if name not in self._bean_definitions:
            raise GlobalException(f"Bean '{name}' 未注册")

        definition = self._bean_definitions[name]

        if definition.scope == BeanScope.SINGLETON.value:
            if name not in self._singleton_instances:
                with self._lock:
                    if name not in self._singleton_instances:
                        self._singleton_instances[name] = definition.bean_class(**kwargs)
            return self._singleton_instances[name]

        if definition.scope == BeanScope.PROTOTYPE.value:
            return definition.bean_class(**kwargs)

        raise GlobalException(f"不支持的作用域: {definition.scope}")


# 兼容历史命名
BeanFactory = Container

# 全局容器实例
application_factory = Container()
domain_service_factory = Container()
repository_factory = Container()
