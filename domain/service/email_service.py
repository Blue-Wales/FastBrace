#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : email_service.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 邮件领域服务（调用三方 SMTP 服务）
"""

from domain.repo.base import BaseRepository
from domain.service.base import BaseService
from domain.value_object.email_message import EmailMessage
from infrastructure.core.container import domain_service_factory
from infrastructure.core.enum_var import BeanScope
from infrastructure.utils.email_utils import EmailSender


@domain_service_factory.autowire("email_domain_service", scope=BeanScope.PROTOTYPE.value)
class SMTPEmailService(BaseService):
    """基于SMTP的邮件服务实现"""

    def __init__(self, repo: BaseRepository | None = None):
        super().__init__(repo)
        self.email_sender = EmailSender()

    def send_email(self, email: EmailMessage) -> bool:
        """发送邮件"""
        return self.email_sender.send_email(
            to=[str(addr) for addr in email.to],
            subject=email.subject,
            body=email.body,
            is_html=email.is_html,
            cc=[str(addr) for addr in email.cc],
            bcc=[str(addr) for addr in email.bcc],
        )
