#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : oss_file_tools.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

from pathlib import Path
from urllib.parse import urljoin

import oss2
from loguru import logger

from infrastructure.core.error_handler import UploadFileError
from infrastructure.core.settings import app_settings
from infrastructure.utils.id_generator import FileIDGenerator


def _get_bucket() -> oss2.Bucket:
    """初始化 OSS Bucket 客户端。"""
    storage = app_settings.object_storage
    auth = oss2.Auth(storage.access_key, storage.secret_key)
    return oss2.Bucket(auth, storage.endpoint, storage.bucket_name)


def _build_object_key(file_name: str, file_type: int) -> str:
    """生成 OSS 对象 Key。"""
    extension = Path(file_name).suffix
    key_value = f"{FileIDGenerator()()}{extension}"
    typed_path = urljoin(f"{file_type}/", key_value)
    return urljoin(app_settings.object_storage.upload_path, typed_path)


def _build_file_url(object_key: str) -> str:
    """生成文件对外访问地址。"""
    object_domain = app_settings.object_storage.object_domain.rstrip("/") + "/"
    return urljoin(object_domain, object_key)


def upload_file(
    file_streams: bytes,
    file_name: str,
    file_size: int,
    file_type: int,
    other_policy: dict | None = None,
) -> str:
    """
    上传文件到阿里云 OSS。

    `other_policy` 参数仅为兼容历史调用保留，OSS 上传当前不使用该参数。
    """
    try:
        object_key = _build_object_key(file_name, file_type)
        result = _get_bucket().put_object(object_key, file_streams)
        if result.status == 200:
            file_path = _build_file_url(object_key)
            logger.info("file: {} upload success", file_name)
            return file_path

        logger.error("file: {} upload failed, status: {}", file_name, result.status)
        raise UploadFileError(message=f"OSS 上传失败，状态码: {result.status}")
    except Exception as e:
        logger.error("file: {} upload failed message {}", file_name, e)
        raise UploadFileError(str(e))


def upload_video(
    file_streams: bytes,
    file_name: str,
    file_size: int,
    file_type: int,
):
    """上传视频文件到阿里云 OSS。"""
    file_path = upload_file(
        file_streams=file_streams,
        file_name=file_name,
        file_size=file_size,
        file_type=file_type,
    )
    if not file_path:
        raise UploadFileError("OSS 视频上传失败")
    return file_path


def batch_delete(keys):
    """
    批量删除 OSS 对象。
    """
    try:
        result = _get_bucket().batch_delete_objects(keys)
        if result.status == 200:
            logger.info("keys: [{}] delete success", ",".join(keys))
        else:
            logger.error("keys: [{}] delete failed, status: {}", ",".join(keys), result.status)
    except Exception as e:
        logger.error("keys: [{}] delete failed message {}", ",".join(keys), e)
