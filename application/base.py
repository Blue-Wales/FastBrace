#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : base.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 应用服务基类与通用响应生成能力
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Protocol

from loguru import logger
from pydantic import BaseModel
from redis import StrictRedis
from sqlalchemy.orm import Session
from infrastructure.utils.cache import redis_db as global_redis_pool
from api.response_body.json_response import (
    BaseResponseModel,
    PagedDataModel,
    PaginationResponseModel,
    ResponseListModel,
    ResponseModel,
)


class IBaseApplicationService(Protocol):
    """应用服务基础接口"""

    db: Session
    redis_client: StrictRedis

    async def transaction(self, session: Session) -> AsyncGenerator[Session, None]:
        """嵌套事务保存点功能"""
        ...


    @staticmethod
    async def generate_page_response(
        page: int, page_size: int, total: int, items: list, item_class: BaseModel
    ) -> PaginationResponseModel:
        """生成分页响应"""
        ...


    @staticmethod
    async def generate_response(data: Any, data_class=BaseResponseModel) -> ResponseModel:
        """生成响应"""
        ...


    @staticmethod
    async def generate_list_response(items: list, item_class: BaseModel) -> ResponseListModel:
        """生成列表响应"""
        ...


class BaseApplicationService:
    """DDD 应用服务基类"""

    def __init__(self, db: Session, redis_client: StrictRedis | None = None):
        self.db = db
        self.redis_client = redis_client
        if self.redis_client is None and global_redis_pool is not None:
            self.redis_client = StrictRedis(connection_pool=global_redis_pool)


    @asynccontextmanager
    async def transaction(self, session):
        """嵌套事务保存点功能"""
        try:
            await session.begin()
            yield session
        except Exception as e:


            logger.error(f"事务执行失败: {e}")
            raise e


    @staticmethod
    async def generate_page_response(page, page_size, total, items, item_class):
        """生成分页响应"""
        response_model = PaginationResponseModel
        page_data = PagedDataModel(
            total=total,
            page=page,
            page_size=page_size,
            items=[item_class(**item.model_dump()) for item in items],


        )
        return response_model(data=page_data)


    @staticmethod
    async def generate_response(data, data_class=BaseResponseModel):
        """生成响应"""
        response_model = ResponseModel
        if data_class is BaseResponseModel:


            return response_model(data=data_class(result=data).model_dump())
        return response_model(data=data_class(**data.model_dump()).model_dump())


    @staticmethod
    async def generate_list_response(items, item_class):
        """生成列表响应"""
        response_model = ResponseListModel
        data_list = [item_class(**item.model_dump()) for item in items]
        return response_model(data=data_list)
