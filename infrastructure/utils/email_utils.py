#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : email_utils.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

import smtplib
import traceback
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from loguru import logger

from infrastructure.core.settings import app_settings
from infrastructure.utils.retry_utils import retry, when_exceptions_type


class EmailSender:
    """邮件发送器"""

    @retry(
        retry_when=when_exceptions_type(
            (
                ConnectionError,  # 连接错误
                TimeoutError,  # 超时错误
                OSError,  # 操作系统错误（包括网络）
                smtplib.SMTPConnectError,  # SMTP连接错误
                smtplib.SMTPServerDisconnected,  # SMTP服务器断开
            )
        ),
        retry_times=3,
        retry_interval=5,
        hooks={
            "on_retry": lambda args, kwargs, outcome, exception: logger.warning(
                f"邮件发送失败，正在重试: {type(exception).__name__}: {exception}"
            )
        },
    )
    def _retrysend_email(
        self,
        to: list[str],
        subject: str,
        body: str,
        is_html: bool = False,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
    ) -> bool:
        """发送邮件"""
        # 创建邮件消息
        msg = MIMEMultipart()

        # 正确设置From头部
        msg["From"] = formataddr((app_settings.email.sender_name, app_settings.email.username))

        # 设置收件人和主题
        msg["To"] = ", ".join(to)
        msg["Subject"] = Header(subject, "utf-8")

        # 抄送设置
        if cc:
            msg["Cc"] = ", ".join(cc)
        if bcc:
            msg["Bcc"] = ", ".join(bcc)

        # 邮件正文
        content_type = "html" if is_html else "plain"
        msg.attach(MIMEText(body, content_type, "utf-8"))

        logger.debug(
            f"邮件内容: to:{to}, subject:{subject}, body:{body}, "
            f"is_html:{is_html}, cc:{cc}, bcc:{bcc}"
        )
        # 建立连接
        with smtplib.SMTP_SSL(
            app_settings.email.smtp_server, app_settings.email.smtp_port, timeout=30
        ) as server:
            server.login(app_settings.email.username, app_settings.email.password)

            # 收件人列表
            recipients = to.copy()
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)

            # 发送邮件
            server.sendmail(app_settings.email.username, recipients, msg.as_string())
            server.quit()

        logger.info(f"邮件发送成功: {subject} -> {[str(email) for email in to]}")
        return True

    def send_email(
        self,
        to: list[str],
        subject: str,
        body: str,
        is_html: bool = False,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
    ) -> bool:
        """发送邮件"""
        try:
            return self._retrysend_email(to, subject, body, is_html, cc, bcc)
        except Exception as e:
            logger.error(f"邮件发送失败，未知错误: {e}, traceback: {traceback.format_exc()}")
            return False
