#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : cron_task_config.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

from celery.schedules import crontab
from pydantic import BaseModel, Field


class RedBeatTaskConfig(BaseModel):
    """
    基于 crontab 的 RedBeat 定时任务配置模型
    """

    name: str = Field(..., description="任务唯一标识")
    task: str = Field(..., description="Celery 任务路径，例如 'tasks.example_task'")
    cron: crontab = Field(..., description="crontab 调度规则")
    args: list | None = Field(default_factory=list)
    kwargs: dict | None = Field(default_factory=dict)
    enabled: bool | None = Field(default=True, description="是否启用该任务")

    class Config:
        arbitrary_types_allowed = True
