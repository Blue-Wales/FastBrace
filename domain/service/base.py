#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : base.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 基础领域服务
"""

from domain.repo.base import BaseRepository


class BaseService:
    def __init__(self, repo: BaseRepository | None = None):
        self.repo = repo
