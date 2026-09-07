#!/usr/bin/env python
"""
@Author: lt
@Date: 2025-06-23
@Desc: 发送邮件事件处理器
"""

from typing import ClassVar

from loguru import logger

from domain.events.user_events import UserEventType
from domain.service.interfaces.email import IEmailService
from domain.value_object.email_message import EmailMessage
from infrastructure.core.container import domain_service_factory
from infrastructure.events.base import BaseEventHandler, DomainEvent
from infrastructure.events.event_bus_service import EventBusService
from infrastructure.utils.template_render import TemplateRender


class EmailTemplateManager:
    """邮件模板管理器"""

    EMAIL_TYPE_MAP: ClassVar[dict] = {
        UserEventType.CREATED.value: {
            "subject": {
                "template": "create_user_email_subject.j2",
                "params": {
                    "company_name": "company_name",
                },
            },
            "body": {
                "template": "create_user_email_body.j2",
                "params": {
                    "name": "name",
                    "username": "username",
                    "password": "plain_password",
                    "login_url": "login_url",
                },
            },
        }
    }

    def __init__(self):
        self.template_render = TemplateRender(topic="email")

    @classmethod
    def _extract_params(cls, event_type: str, position: str, event_data: dict) -> dict:
        """提取事件数据中的参数"""
        params = {}
        for key, value in cls.EMAIL_TYPE_MAP[event_type][position]["params"].items():
            params[key] = event_data[value]
        return params

    def render_template(self, event_type: str, event_data: dict) -> tuple[str, str]:
        """渲染邮件模板"""
        try:
            subject_params = self._extract_params(event_type, "subject", event_data)
            body_params = self._extract_params(event_type, "body", event_data)
        except KeyError as e:
            logger.error(f"事件数据中缺少参数: {e}")
            raise

        subject = self.template_render.render_template(
            self.EMAIL_TYPE_MAP[event_type]["subject"]["template"], **subject_params
        )
        body = self.template_render.render_template(
            self.EMAIL_TYPE_MAP[event_type]["body"]["template"], **body_params
        )

        return subject, body


@EventBusService.subscribe("Email", is_local=False)
class EmailSendEventHandler(BaseEventHandler):
    """发送邮件事件处理器"""

    __type__ = "email_send_handler"
    SUPPORTED_EVENT_TYPES: ClassVar[list[str]] = [UserEventType.CREATED.value]

    def __init__(self):
        # 定义支持的事件类型
        super().__init__()

        self.email_service: IEmailService = domain_service_factory.get_bean("email_domain_service")
        self.email_template_manager = EmailTemplateManager()

    def _handle_event(self, event: DomainEvent) -> None:
        """处理用户相关事件"""
        subject, body = self.email_template_manager.render_template(
            event.event_type, event.event_data
        )
        self.email_service.send_email(
            EmailMessage(
                to=[event.event_data["email"]],
                subject=subject,
                body=body,
            )
        )
