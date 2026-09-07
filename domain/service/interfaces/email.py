#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : email.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 邮件领域服务接口
"""

from typing import Protocol, runtime_checkable

from domain.value_object.email_message import EmailMessage


@runtime_checkable
class IEmailService(Protocol):
    """邮件消息发送契约。

    事件处理器和应用服务只依赖该契约，不感知 SMTP 、重试或连接配置细节。
    Protocol 可在运行时检查，便于事件处理器验证容器返回的实现。
    """

    def send_email(self, email: EmailMessage) -> bool:
        """发送一封已完成校验的邮件消息。

        Args:
            email: 包含收件人、主题、正文、抄送、密送和正文类型的邮件值对象。

        Returns:
            邮件供应端确认发送成功时返回 `True`，否则返回 `False`。

        Raises:
            Exception: 具体实现未吸收的配置、连接或消息格式异常。
        """
        ...
