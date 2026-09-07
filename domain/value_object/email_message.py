#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : email_message.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 邮件消息值对象
"""

from itertools import chain

from pydantic import BaseModel, EmailStr, Field, field_validator


class EmailAttachment(BaseModel):
    """邮件附件值对象"""

    filename: str = Field(..., description="文件名")
    content: bytes = Field(..., description="文件内容")
    content_type: str = Field(default="application/octet-stream", description="MIME类型")

    class Config:
        frozen = True

    def __hash__(self):
        """为附件提供哈希支持，使其可以用于set()去重"""
        return hash((self.filename, self.content, self.content_type))


class EmailMessage(BaseModel):
    """
    邮件消息值对象

    特征：
    - 不可变：一旦创建后不能修改
    - 无唯一标识：通过属性值来识别
    - 值相等：相同内容的邮件消息被认为是相等的
    """

    to: list[EmailStr] = Field(..., description="收件人邮箱列表")
    subject: str = Field(..., description="邮件主题")
    body: str = Field(..., description="邮件正文")
    is_html: bool = Field(default=False, description="是否为HTML格式")
    cc: list[EmailStr] = Field(default_factory=list, description="抄送邮箱列表")
    bcc: list[EmailStr] = Field(default_factory=list, description="密送邮箱列表")
    attachments: list[EmailAttachment] = Field(default_factory=list, description="附件列表")

    class Config:
        frozen = True  # 设置为不可变

    @field_validator("to")
    @classmethod
    def validate_to_not_empty(cls, v):
        """验证收件人列表不为空"""
        if not v or len(v) == 0:
            raise ValueError("收件人列表不能为空")
        return v

    @field_validator("subject")
    @classmethod
    def validate_subject_not_empty(cls, v):
        """验证邮件主题不为空"""
        if not v or len(v.strip()) == 0:
            raise ValueError("邮件主题不能为空")
        return v.strip()

    @property
    def all_recipients(self) -> list[str]:
        """获取所有收件人（包括to、cc、bcc）"""
        return list(set(chain(self.to, self.cc, self.bcc)))

    @property
    def has_attachments(self) -> bool:
        """检查是否有附件"""
        return len(self.attachments) > 0

    def with_attachment(self, attachment: EmailAttachment) -> "EmailMessage":
        """
        添加附件并返回新的邮件消息对象（值对象不可变原则）
        """
        return EmailMessage(
            to=self.to,
            subject=self.subject,
            body=self.body,
            is_html=self.is_html,
            cc=self.cc,
            bcc=self.bcc,
            attachments=list(set(chain(self.attachments, [attachment]))),
        )

    def with_cc(self, cc_emails: list[EmailStr]) -> "EmailMessage":
        """
        添加抄送并返回新的邮件消息对象
        """
        return EmailMessage(
            to=self.to,
            subject=self.subject,
            body=self.body,
            is_html=self.is_html,
            cc=list(set(chain(self.cc, cc_emails))),
            bcc=self.bcc,
            attachments=self.attachments,
        )

    def with_bcc(self, bcc_emails: list[EmailStr]) -> "EmailMessage":
        """
        添加密送并返回新的邮件消息对象
        """
        return EmailMessage(
            to=self.to,
            subject=self.subject,
            body=self.body,
            is_html=self.is_html,
            cc=self.cc,
            bcc=list(set(chain(self.bcc, bcc_emails))),
            attachments=self.attachments,
        )
