#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : file.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 文件上传下载接口
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK

from api.request_body.file_request import UploadFileRequest
from api.response_model.common_res_model import FileResModel
from infrastructure.core.container import application_factory
from infrastructure.utils.database import get_db
from infrastructure.utils.oauth2_tools import oauth2_scheme
from infrastructure.utils.response_model_generator import generate_response_model

file_router = APIRouter()


@file_router.post(
    "/upload",
    summary="上传文件",
    dependencies=[Depends(oauth2_scheme)],
    response_model=generate_response_model(FileResModel, "upload_file"),
)
async def upload_file(
    request_data: Annotated[UploadFileRequest, Form()],
    db: Session = Depends(get_db),
):
    """上传文件"""

    app_service = application_factory.get_bean("file_app_service", db=db)

    result = await app_service.upload_file(
        file_obj=request_data.file, file_type=request_data.file_type
    )

    return JSONResponse(status_code=HTTP_200_OK, content=result)
