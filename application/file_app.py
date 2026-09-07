#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : file_app.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 文件应用服务
"""

from fastapi import UploadFile

from api.response_body.json_response import ResponseModel
from application.base import BaseApplicationService
from infrastructure.core.container import application_factory
from infrastructure.core.enum_var import BeanScope, FileType
from infrastructure.core.error_handler import NotFoundError
from infrastructure.utils import oss_file_tools


@application_factory.autowire("file_app_service", scope=BeanScope.PROTOTYPE.value)
class FileApplicationService(BaseApplicationService):
    """文件相关的应用服务"""

    async def upload_file(self, file_obj: UploadFile, file_type: str):
        """上传文件到 OSS"""
        file_name = file_obj.filename
        file_size = file_obj.size
        if file_type in FileType.__members__:
            file_type = FileType[file_type].value
        else:
            raise NotFoundError(f"{file_type} 文件类型不在规定范围内")
        content = await file_obj.read()

        if file_obj.content_type in ["video/quicktime", "video/mp4"]:
            result = oss_file_tools.upload_video(
                file_streams=content, file_name=file_name, file_size=file_size, file_type=file_type
            )
        else:
            result = oss_file_tools.upload_file(
                file_streams=content, file_name=file_name, file_size=file_size, file_type=file_type
            )

        data = ResponseModel(data={"file_name": file_name, "file_path": result})
        return data.model_dump()
