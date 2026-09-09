#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : database.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

import traceback
from contextlib import contextmanager

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, declarative_base, scoped_session, sessionmaker

from infrastructure.core.error_handler import DuplicateEntryError

session_maker_local: scoped_session[Session] | None = None

Base = declarative_base()


def init_database(db: BaseModel):
    """
    初始化异步数据库连接池并创建会话工厂。

    :param db: 包含数据库连接参数的字典，必需包含驱动名称(drivername)、用户名(username)、
                    密码(password)、主机(host)、端口(port)和数据库名称(database)等键。
    :return:
    """
    global session_maker_local
    db_url = URL.create(
        drivername=db.drivername,
        username=db.username,
        password=db.password,
        host=db.host,
        port=db.port,
        database=db.database,
    )

    # 创建数据库引擎并配置连接池参数
    engine = create_engine(
        db_url,
        pool_size=15,  # 连接池基础大小
        max_overflow=5,  # 允许超过pool_size的最大连接数
        pool_recycle=3600,  # 连接回收时间（秒）
        pool_pre_ping=True,  # 连接使用前主动检测有效性
    )

    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # 创建数据库会话工厂并绑定引擎
    session_maker_local = scoped_session(session_factory)

    return engine


async def get_db():
    """
    获取数据库会话。
    """
    if session_maker_local is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    db = session_maker_local()
    try:
        yield db
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if "Duplicate entry" in str(e):
            logger.debug(f"重复信息插入: {e}，traceback: {traceback.format_exc()}")
            raise DuplicateEntryError("重复信息插入")
        else:
            logger.error(f"数据库插入错误: {e}，traceback: {traceback.format_exc()}")
            raise e
    except Exception as e:
        logger.error(f"异常信息: {e}，traceback: {traceback.format_exc()}")
        db.rollback()
        raise
    finally:
        session_maker_local.remove()


@contextmanager
def celery_db():
    """
    获取数据库会话。
    """
    if session_maker_local is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    db = session_maker_local()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"{e}")
        db.rollback()
        raise
    finally:
        session_maker_local.remove()
