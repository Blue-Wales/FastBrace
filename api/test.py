#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : test.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 测试辅助接口（仅非生产环境注册）
"""

import datetime

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from infrastructure.core.settings import app_settings

test_router = APIRouter()


@test_router.post("/", include_in_schema=False)
async def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """生成一个临时 token，用于本地联调测试"""
    if form_data.username != "licong" or form_data.password != "123456":
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = jwt.encode(
        payload={
            "user_id": "567241090000748585",
            "exp": (
                datetime.datetime.utcnow()
                + datetime.timedelta(seconds=app_settings.jwt.expire_time)
            ),
            "user_name": "李聪",
        },
        key=app_settings.jwt.secret_key,
        algorithm=app_settings.jwt.algorithm,
    )
    return {"access_token": token, "token_type": "bearer"}
