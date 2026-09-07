#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : permission_checker.py
@Author  : bright
@Date    : 2026-08-22
"""

from abc import ABC, abstractmethod

from loguru import logger

from infrastructure.core.enum_var import PermissionLevel, Permissions


class PermissionExpression(ABC):
    """权限表达式抽象基类"""

    @abstractmethod
    def evaluate(self, user_permissions: dict[str, list[int]]) -> bool:
        """评估权限表达式"""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """字符串表示"""
        pass

    def __and__(self, other: "PermissionExpression") -> "AndExpression":
        """与操作"""
        return AndExpression(self, other)

    def __or__(self, other: "PermissionExpression") -> "OrExpression":
        """或操作"""
        return OrExpression(self, other)


class Permission(PermissionExpression):
    """单个权限类"""

    def __init__(self, module_name: Permissions, level: PermissionLevel):
        """
        初始化权限

        :param module_name: 模块名称
        :param level: 权限级别 (1-查看, 2-编辑, 3-导出)
        """
        self.module_name = module_name.value
        self.level = level.value

        # 验证权限级别
        if self.level not in [1, 2, 3]:
            raise ValueError(f"无效的权限级别: {level}, 必须是1、2或3")

    def evaluate(self, user_permissions: dict[str, list[int]]) -> bool:
        """
        评估用户是否有此权限

        :param user_permissions: 用户权限字典，格式：{"模块名": [级别列表]}
        :return: 是否有权限
        """
        if self.module_name not in user_permissions:
            return False

        return self.level in user_permissions[self.module_name]

    def __str__(self) -> str:
        """字符串表示"""
        level_names = {1: "查看", 2: "编辑", 3: "导出"}
        level_name = level_names.get(self.level, f"级别{self.level}")
        return f"Permission({self.module_name}, {level_name})"

    def __repr__(self) -> str:
        return self.__str__()


class AndExpression(PermissionExpression):
    """与表达式"""

    def __init__(self, left: PermissionExpression, right: PermissionExpression):
        self.left = left
        self.right = right

    def evaluate(self, user_permissions: dict[str, list[int]]) -> bool:
        """与操作：两个表达式都为真才返回真"""
        return self.left.evaluate(user_permissions) and self.right.evaluate(user_permissions)

    def __str__(self) -> str:
        return f"({self.left} & {self.right})"


class OrExpression(PermissionExpression):
    """或表达式"""

    def __init__(self, left: PermissionExpression, right: PermissionExpression):
        self.left = left
        self.right = right

    def evaluate(self, user_permissions: dict[str, list[int]]) -> bool:
        """或操作：任一表达式为真就返回真"""
        return self.left.evaluate(user_permissions) or self.right.evaluate(user_permissions)

    def __str__(self) -> str:
        return f"({self.left} | {self.right})"


class PermissionChecker:
    """权限检查器"""

    @staticmethod
    def check(expression: PermissionExpression, user_permissions: dict[str, list[int]]) -> bool:
        """
        检查权限表达式

        :param expression: 权限表达式
        :param user_permissions: 用户权限字典
        :return: 是否有权限
        """
        try:
            result = expression.evaluate(user_permissions)
            logger.info(f"权限检查: {expression} -> {result}")
            return result
        except Exception as e:
            logger.error(f"权限检查出错: {expression}, 错误: {e}")
            return False

    @staticmethod
    def get_required_permissions(expression: PermissionExpression) -> set[str]:
        """
        获取表达式中涉及的所有模块名称

        :param expression: 权限表达式
        :return: 模块名称集合
        """
        def _extract_modules(expr: PermissionExpression) -> set[str]:
            if isinstance(expr, Permission):
                return {expr.module_name}
            if isinstance(expr, (AndExpression, OrExpression)):
                return _extract_modules(expr.left) | _extract_modules(expr.right)
            return set()

        return _extract_modules(expression)


# 便捷函数
def P(module_name: Permissions, level: PermissionLevel) -> Permission:
    """创建权限的便捷函数"""
    return Permission(module_name, level)


def check_permission(
    expression: PermissionExpression, user_permissions: dict[str, list[int]]
) -> bool:
    """检查权限的便捷函数"""
    return PermissionChecker.check(expression, user_permissions)
