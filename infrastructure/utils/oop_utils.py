#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : oop_utils.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

import sys
from abc import ABC, ABCMeta, abstractmethod
from collections.abc import Callable
from typing import Any


def import_class(module_path: str, class_name: str | None = None) -> Any:
    """根据形如"a.b.c"的路径获取一个已定义的类

    如果目标路径或类不存在，则返回None

    :param module_path: 模块路径，如：a.b.c
    :param class_name: 类名，如果传None，则以module_path的最后一段作为类名
        如：a.b.ClassB，则取a.b为模块路径，ClassB为类名
    :return:
    """
    try:
        __import__(module_path)
    except ImportError:
        return None

    if not class_name:
        class_name = module_path.split(".")[-1]

    try:
        a_module = sys.modules[module_path]
        a_class = getattr(a_module, class_name)
    except (KeyError, AttributeError):
        return None

    return a_class


class NeedImplemented:
    """
    使用该类标识未继承的类属性

    配合ClsAttrCheckMixin类，被标记的属性若子类未继承，则会抛出NotImplementedError异常
    如：
        class Base(ABC, ClsAttrCheckMixin):
            attr1 = NeedImplemented()

        class A(Base):
            attr1 = 'A'
    """


class ClsAttrCheckMixin:
    """Mixin类，为类赋予检测子类是否继承指定类属性的能力

    !!! 注：父类必须以Base开头，当继承此类的类名不以Base开头时，
    会检查类中为NeedImplemented类型的类属性，检查到该属性则会抛出异常

    """

    def __init_subclass__(cls, **kwargs):
        if cls.__name__.startswith("Base"):
            return

        for name in dir(cls):
            try:
                attr = getattr(cls, name)
            except AttributeError:
                continue

            if isinstance(attr, NeedImplemented):
                raise NotImplementedError(f"The attribute {name} need to be implemented!")


class Factory:
    """工厂类"""

    def __init__(self):
        self.cls_map = {}

    def has(self, cls_name: Any) -> bool:
        return cls_name in self.cls_map

    def get_class(self, cls_name: Any) -> Any:
        if cls_name not in self.cls_map:
            return None

        return self.cls_map[cls_name]

    def get_instance(self, cls_name: Any, *args, **kwargs) -> Any:
        cls = self.get_class(cls_name)
        if not cls:
            return None

        return cls(*args, **kwargs)

    def register(self, cls_name: Any, cls: str | Any) -> None:
        """注册类

        :param cls_name: 类注册名
        :param cls: 注册类，两种方式：
            1.直接传类
            2.传递类的路径，如：a.b.ClassB
        :return:
        """
        if isinstance(cls, str):
            cls = import_class(cls)

        self.cls_map[cls_name] = cls

    def __call__(self, cls_name, *args, **kwargs):
        return self.get_instance(cls_name, *args, **kwargs)


def build_fac(identifier: str, *base_classes: type) -> Callable:
    """工厂方法生成器

    基于基类生成所有自子类的工厂方法

    **注意！！**： 使用该方法构造工厂类需要先导入所有已继承该基类的子类，这样才能找到所有子类并注册

    :param identifier: 类属性标志位，用于索引子类，如：
        class A:
            __id__ = ''

        class B(A):
            __id__ = 'class B'

        class C(A):
            __id__ = 'class C'

        fac = gen_fac('__id__', A)
        b = fac('class B')
        b_cls = fac.get_class('class B')
    :param base_classes: Base class
    :return: factory function
    """
    subclasses = []
    for parent_cls in base_classes:
        subclasses.extend(parent_cls.__subclasses__())

    fac = Factory()
    for sub_cls in subclasses:
        fac.register(getattr(sub_cls, identifier), sub_cls)

    return fac


class Publisher:
    def __init__(self, *args, **kwargs):
        self._observers = []

    def add_observer(self, observer):
        if observer in self._observers:
            return

        self._observers.append(observer)

    def remove_observer(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            return

    def notify(self, channel: str, **kwargs):
        for obs in self._observers:
            if channel not in obs.channels:
                continue

            obs.action(self, channel, **kwargs)


class Observer(ABC):
    # ！！该属性用于识别需要执行的通知，子类继承需要重写
    channels = ()

    @abstractmethod
    def action(self, publisher, channel: str, **kwargs):
        pass


class DataDescriptor:
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class SingletonMeta(type):
    """单例模式元类"""

    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance


class ABCSingletonMeta(ABCMeta):
    """单例模式元类"""

    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance
