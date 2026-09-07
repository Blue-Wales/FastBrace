#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : user_events.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 用户领域事件
"""

from enum import Enum

from infrastructure.events.base import DomainEvent


class UserEventType(Enum):
    """用户事件类型"""

    CREATED = "user.created"
    PASSWORD_CHANGED = "user.password_changed"
    STATUS_CHANGED = "user.status_changed"
    DELETED = "user.deleted"


class _BaseUserEvent(DomainEvent):
    """用户事件基类"""

    aggregate_type: str = "User"
    is_local: bool = False


class UserCreatedEvent(_BaseUserEvent):
    """用户创建事件"""

    event_type: str = UserEventType.CREATED.value


class UserPasswordChangedEvent(_BaseUserEvent):
    """用户密码修改事件"""

    event_type: str = UserEventType.PASSWORD_CHANGED.value


class UserStatusChangedEvent(_BaseUserEvent):
    """用户状态变更事件"""

    event_type: str = UserEventType.STATUS_CHANGED.value


class UserDeletedEvent(_BaseUserEvent):
    """用户删除事件"""

    event_type: str = UserEventType.DELETED.value
