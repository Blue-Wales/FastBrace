#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : settings.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 框架配置管理
"""

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, RootModel, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class JWTSettings(BaseModel):
    """JWT 认证配置。"""

    secret_key: str
    algorithm: str
    expire_time: int
    refresh_expire_time: int


class RedisDB(BaseModel):
    """Redis 连接配置。"""

    host: str
    port: int
    password: str


class Database(BaseModel):
    """数据库连接配置。"""

    drivername: str
    host: str
    port: int
    username: str
    password: str
    database: str


class ObjectStorage(BaseModel):
    """文件上传对象存储配置。"""

    access_key: str
    secret_key: str
    endpoint: str
    bucket_name: str
    object_domain: str
    watermark_template: str = ""
    upload_path: str = ""


class RSASettings(BaseModel):
    """安全通信所需的 RSA 加密配置。"""

    private_key: str
    key_size: int = 2048
    enabled: bool = True


class LogSettings(BaseModel):
    """日志配置。"""

    log_dir: str
    log_name: str
    debug: bool = False
    log_rotation: str = "200 MB"
    log_retention: int = 5
    error_log_rotation: str = "100 MB"
    error_log_retention: int = 3
    use_async_logging: bool = False


class EmailSettings(BaseModel):
    """邮件服务配置。"""

    smtp_server: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True
    sender_name: str = "FastBrace"
    company_name: str = "FastBrace"


class CeleryBeatConfig(BaseModel):
    """Celery Beat 调度器配置。"""

    scheduler: str
    beat_max_loop_interval: int
    beat_sync_every: int
    key_prefix: str
    module_path: str


class CeleryConfig(BaseModel):
    """Celery 任务队列配置。"""

    broker_url: str = "redis://:{redis_password}@{redis_host}:{redis_port}/2"
    result_backend: str = "redis://:{redis_password}@{redis_host}:{redis_port}/3"
    result_expires: int = 60 * 60 * 24
    task_serializer: str = "json"
    accept_content: list[str] = ["json"]
    result_serializer: str = "json"
    enable_utc: bool = False
    timezone: str = "Asia/Shanghai"
    task_track_started: bool = True
    task_publish_retry: bool = True
    task_publish_retry_policy: dict[str, Any] = {
        "max_retries": 3,
        "interval_start": 0,
        "interval_step": 0.5,
        "interval_max": 3.0,
    }
    beat: CeleryBeatConfig


class EventBusSettings(BaseModel):
    """领域事件总线配置。"""

    local_transport_type: str = "memory"
    cross_domain_transport_type: str = "celery"
    name: str = "vben-fastapi-framework"
    enable_event_store: bool = False
    local_event_bus_concurrency: int = Field(default=0, ge=0)
    cross_domain_event_bus_concurrency: int = Field(default=0, ge=0)


# ============================================================
# 短信配置
# ============================================================


class SMS(RootModel[dict[int | str, Any]]):
    """短信服务配置，支持供应商自定义字段。"""

    def __getitem__(self, key: Any) -> Any:
        if key in self.root:
            return self.root[key]
        return self.root.get(str(key))

    @property
    def access_key_id(self) -> Any:
        return self.root.get("access_key_id")

    @property
    def secret_access_key(self) -> Any:
        return self.root.get("secret_access_key")


class SMSCode(BaseModel):
    """短信模板编码配置。"""

    default: str = ""
    verification: str = ""
    notification: str = ""
    reminder: str = ""


class SMSErrCodes(RootModel[dict[str, str]]):
    """短信错误码映射。"""

    pass


# ============================================================
# 应用配置
# ============================================================


class AppSettings(BaseSettings):
    """从 YAML 文件加载的主应用配置。"""

    login_url: str

    service_name: str

    service_version: str

    db: Database

    api_log: LogSettings

    event_log: LogSettings

    cron_log: LogSettings

    exclude_path: list[str]

    object_storage: ObjectStorage

    redis_db: RedisDB

    jwt: JWTSettings

    rsa: RSASettings

    email: EmailSettings

    env: str = os.getenv("ENV", "dev")

    event_bus: EventBusSettings

    celery: CeleryConfig

    sms: SMS
    sms_code: SMSCode
    sms_err_codes: SMSErrCodes

    model_config = SettingsConfigDict(
        yaml_file=Path(__file__).parents[1]
        / "config"
        / "settings.{}.yaml".format(os.getenv("ENV", "dev")),
        yaml_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """优先使用环境变量覆盖 YAML 配置，便于生产环境注入敏感信息。"""
        return (
            env_settings,
            YamlConfigSettingsSource(settings_cls),
        )

    @model_validator(mode="after")
    def validate_celery_config(self):
        """将 Redis 连接信息填充到 Celery 地址模板。"""
        self.celery.broker_url = self.celery.broker_url.format(
            redis_password=self.redis_db.password,
            redis_host=self.redis_db.host,
            redis_port=self.redis_db.port,
        )
        self.celery.result_backend = self.celery.result_backend.format(
            redis_password=self.redis_db.password,
            redis_host=self.redis_db.host,
            redis_port=self.redis_db.port,
        )
        return self


app_settings = AppSettings()
