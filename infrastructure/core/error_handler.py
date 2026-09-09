#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : error_handler.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 框架异常处理
"""

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from infrastructure.core.enum_var import ErrorCode

# =============================================================================
# 基础异常
# =============================================================================


class OrangeCraftException(Exception):
    """框架异常基类。"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# =============================================================================
# 应用异常
# =============================================================================


class GlobalException(OrangeCraftException):
    """通用应用异常。"""

    pass


class APIRequestError(OrangeCraftException):
    """外部接口请求失败。"""

    pass


class UploadFileError(OrangeCraftException):
    """文件上传失败。"""

    pass


# =============================================================================
# 资源异常
# =============================================================================


class NotFoundError(OrangeCraftException):
    """请求的资源不存在。"""

    def __init__(self, message: str, status_code: int = 404):
        super().__init__(message, status_code)


class DeleteError(OrangeCraftException):
    """资源删除失败。"""

    pass


class DuplicateEntryError(OrangeCraftException):
    """数据重复。"""

    pass


# =============================================================================
# 认证与授权异常
# =============================================================================


class AuthorizationError(OrangeCraftException):
    """认证或授权失败。"""

    pass


class PermissionDeniedError(OrangeCraftException):
    """权限不足。"""

    def __init__(self, message: str, status_code: int = 403):
        super().__init__(message, status_code)


# =============================================================================
# 校验异常
# =============================================================================


class InvalidInputError(OrangeCraftException):
    """输入数据无效。"""

    pass


class StatusError(OrangeCraftException):
    """状态流转无效。"""

    pass


class NotAllowedOperation(OrangeCraftException):
    """不允许执行该操作。"""

    pass


# =============================================================================
# 异常处理器
# =============================================================================


async def global_exception_handler(request: Request, exc: OrangeCraftException):
    return JSONResponse(
        status_code=200,
        content={
            "code": ErrorCode.internal_error.value,
            "error": "服务器开小差了，需要静静",
            "error_message": exc.message,
        },
    )


async def upload_file_exception_handler(request: Request, exc: UploadFileError):
    return JSONResponse(
        status_code=200,
        content={
            "code": ErrorCode.file_upload_error.value,
            "error": "文件表示它恐高，拒绝上传",
            "error_message": exc.message,
        },
    )


async def api_request_exception_handler(request: Request, exc: APIRequestError):
    return JSONResponse(
        status_code=200,
        content={
            "code": ErrorCode.api_request_error.value,
            "error": "外部接口放了鸽子，没来赴约",
            "error_message": exc.message,
        },
    )


async def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=200,
        content={
            "code": ErrorCode.not_found_error.value,
            "error": "您找的东西去平行宇宙了",
            "error_message": exc.message,
        },
    )


async def delete_exception_handler(request: Request, exc: DeleteError):
    return JSONResponse(
        status_code=200,
        content={
            "code": ErrorCode.delete_error.value,
            "error": "资源赖着不走，可能对您有感情",
            "error_message": exc.message,
        },
    )


async def duplicate_entry_exception_handler(request: Request, exc: DuplicateEntryError):
    return JSONResponse(
        status_code=200,
        content={
            "code": ErrorCode.duplicate_entry_error.value,
            "error": "数据已存在，别让它分身乏术",
            "error_message": exc.message,
        },
    )


async def authorization_exception_handler(request: Request, exc: AuthorizationError):
    return JSONResponse(
        status_code=200,
        content={
            "code": ErrorCode.authorization_error.value,
            "error": "凭证失忆了，请重新证明您是您",
            "error_message": exc.message,
        },
    )


async def status_exception_handler(request: Request, exc: StatusError):
    return JSONResponse(
        status_code=200,
        content={
            "code": ErrorCode.status_error.value,
            "error": "状态君今天心情不好，不按套路出牌",
            "error_message": exc.message,
        },
    )


async def invalid_input_exception_handler(request: Request, exc: InvalidInputError):
    return JSONResponse(
        status_code=200,
        content={
            "code": ErrorCode.invalid_input_error.value,
            "error": "输入有点离谱，服务器表示看不懂",
            "error_message": exc.message,
        },
    )


async def permission_denied_exception_handler(request: Request, exc: PermissionDeniedError):
    return JSONResponse(
        status_code=200,
        content={
            "code": ErrorCode.permission_denied_error.value,
            "error": "权限不足，这件事您说了不算",
            "error_message": exc.message,
        },
    )


async def not_allowed_operation_exception_handler(request: Request, exc: NotAllowedOperation):
    return JSONResponse(
        status_code=200,
        content={
            "code": ErrorCode.not_allowed_operation_error.value,
            "error": "此路不通，换个姿势试试",
            "error_message": exc.message,
        },
    )


def init_error_handler(app: FastAPI):
    """向 FastAPI 应用注册全部异常处理器。"""
    app.add_exception_handler(GlobalException, global_exception_handler)
    app.add_exception_handler(UploadFileError, upload_file_exception_handler)
    app.add_exception_handler(APIRequestError, api_request_exception_handler)
    app.add_exception_handler(NotFoundError, not_found_exception_handler)
    app.add_exception_handler(DeleteError, delete_exception_handler)
    app.add_exception_handler(DuplicateEntryError, duplicate_entry_exception_handler)
    app.add_exception_handler(AuthorizationError, authorization_exception_handler)
    app.add_exception_handler(StatusError, status_exception_handler)
    app.add_exception_handler(InvalidInputError, invalid_input_exception_handler)
    app.add_exception_handler(PermissionDeniedError, permission_denied_exception_handler)
    app.add_exception_handler(NotAllowedOperation, not_allowed_operation_exception_handler)
