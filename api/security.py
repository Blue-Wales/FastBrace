#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : security.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 安全相关接口
"""

from fastapi import APIRouter
from loguru import logger
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK

from api.response_body.json_response import BaseResponseModel
from infrastructure.core.enum_var import ErrorCode
from infrastructure.core.error_handler import GlobalException
from infrastructure.core.settings import app_settings
from infrastructure.utils.response_model_generator import generate_response_model
from infrastructure.utils.rsa_utils import RSAPasswordEncryption

security_router = APIRouter()


@security_router.get(
    "/public-key",
    summary="获取RSA公钥",
    response_model=generate_response_model(BaseResponseModel, "get_public_key"),
)
async def get_public_key():
    """获取用于密码加密的 RSA 公钥

    前端使用此公钥对敏感数据（如密码）进行加密后再传输。
    """
    if not app_settings.rsa.enabled:
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "code": ErrorCode.function_unable_error.value,
                "error": "功能还在开发者的梦里，尚未照进现实",
                "error_message": "RSA加密未启用，请使用明文传输",
            },
        )

    # 创建RSA密码加密管理器
    rsa_manager = RSAPasswordEncryption(app_settings.rsa.private_key)

    # 获取公钥信息
    try:
        public_key_info = rsa_manager.get_public_key_for_frontend()
    except Exception as e:
        logger.debug(f"获取公钥信息失败: {e}")
        raise GlobalException("获取公钥信息失败")

    return JSONResponse(
        status_code=HTTP_200_OK,
        content={
            "code": 200,
            "data": {
                "encryption_enabled": True,
                **public_key_info,
                "usage": "使用此公钥加密密码后再发送登录请求",
            },
        },
    )
