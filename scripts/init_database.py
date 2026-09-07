#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : init_database.py
@Author  : bright
@Date    : 2026-08-25
@Desc    : 数据库初始化脚本，创建数据库、表结构并初始化管理员用户

用法:
    python scripts/init_database.py
"""

import os
import sys
from pathlib import Path

# 保证从任意目录运行脚本时都能导入项目内的 infrastructure 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pymysql
from alembic import command
from alembic.config import Config
from loguru import logger
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from infrastructure.core.app import auto_load_modules
from infrastructure.core.enum_var import PermissionLevel, Permissions
from infrastructure.core.settings import app_settings
from infrastructure.models.role import (
    ADMIN_ROLE_CODE,
    ADMIN_ROLE_ID,
    ADMIN_ROLE_NAME,
    Role,
    RoleClosure,
)
from infrastructure.models.user import User, UserRoleRelations
from infrastructure.utils import database
from infrastructure.utils.admin_constants import (
    ADMIN_EMAIL,
    ADMIN_GENDER,
    ADMIN_MOBILE,
    ADMIN_NAME,
    ADMIN_NICK_NAME,
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
)
from infrastructure.utils.database_util import get_database_url
from infrastructure.utils.password_utils import hash_password


def load_all_models() -> None:
    """加载所有模型，确保 Base.metadata 包含全部表定义。"""
    try:
        auto_load_modules(base_packages=["infrastructure.models"])
        table_names = list(database.Base.metadata.tables.keys())
        logger.info(f"模型加载完成，已注册的表: {', '.join(table_names)}")
    except ImportError as exc:
        logger.warning(f"部分模型加载失败: {exc}")


def get_alembic_config() -> Config:
    """构建 Alembic 配置。"""
    project_root = Path(__file__).resolve().parent.parent
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "infrastructure" / "migrations"))
    config.set_main_option("sqlalchemy.url", get_database_url(escape_percent=True))
    return config


def create_model_tables(engine) -> None:
    """按当前模型创建缺失表，适用于全新环境初始化。"""
    logger.info("开始创建模型表结构...")
    database.Base.metadata.create_all(bind=engine)
    logger.info("模型表结构检查完成")


def has_alembic_version(engine) -> bool:
    """检查数据库是否已有 Alembic 版本表。"""
    return inspect(engine).has_table("alembic_version")


def create_database_if_not_exists() -> None:
    """创建数据库（如果不存在）。"""
    logger.info(f"尝试连接 MySQL 服务器: {app_settings.db.host}:{app_settings.db.port}")

    conn = None
    cursor = None
    try:
        conn = pymysql.connect(
            host=app_settings.db.host,
            port=app_settings.db.port,
            user=app_settings.db.username,
            password=app_settings.db.password,
            charset="utf8mb4",
            autocommit=False,
        )
        logger.info("MySQL 连接成功")

        cursor = conn.cursor()
        cursor.execute(f"SHOW DATABASES LIKE '{app_settings.db.database}'")
        if cursor.fetchone():
            logger.info(f"数据库 '{app_settings.db.database}' 已存在")
            return

        cursor.execute(
            f"CREATE DATABASE `{app_settings.db.database}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conn.commit()
        logger.info(f"数据库 '{app_settings.db.database}' 创建成功")
    except pymysql.Error as exc:
        if conn:
            conn.rollback()
        logger.error(f"MySQL 错误: {exc}")
        raise
    except Exception:
        if conn:
            conn.rollback()
        logger.exception("数据库创建失败")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def run_migrations() -> bool:
    """运行数据库迁移。"""
    logger.info("开始运行数据库迁移...")
    try:
        command.upgrade(get_alembic_config(), "head")
        logger.info("数据库迁移完成")
        return True
    except Exception:
        logger.exception("数据库迁移失败")
        return False


def check_tables() -> bool:
    """检查关键表结构是否就绪。"""
    logger.info("开始检查数据库表结构...")

    if database.session_maker_local is None:
        logger.error("数据库会话未初始化")
        return False

    db = database.session_maker_local()
    try:
        for table in ("user", "roles"):
            result = db.execute(text(f"SHOW TABLES LIKE '{table}'"))
            if result.fetchone():
                logger.info(f"验证: {table} 表已存在")
            else:
                logger.warning(f"警告: {table} 表未找到")
        return True
    except Exception:
        logger.exception("验证表结构失败")
        return False
    finally:
        database.session_maker_local.remove()


def init_admin_user() -> bool:
    """使用 SQLAlchemy ORM 初始化超级管理员用户，支持断点续跑。"""
    logger.info("开始初始化超级管理员用户...")

    if database.session_maker_local is None:
        logger.error("数据库未初始化")
        return False

    db = database.session_maker_local()
    try:
        # 角色已存在视为已初始化过
        admin_role = db.query(Role).filter(Role.entity_id == ADMIN_ROLE_ID).first()
        if admin_role:
            logger.info("超级管理员角色已存在，跳过初始化")
            return True

        # 1. 创建超级管理员角色
        permissions = {
            permission.value: [
                PermissionLevel.VIEW.value,
                PermissionLevel.EDIT.value,
                PermissionLevel.EXPORT.value,
            ]
            for permission in Permissions
        }
        db.add(
            Role(
                entity_id=ADMIN_ROLE_ID,
                code=ADMIN_ROLE_CODE,
                name=ADMIN_ROLE_NAME,
                permissions=permissions,
            )
        )
        logger.info("创建超级管理员角色")

        # 2. 创建角色层级关系（超级管理员为根角色）
        if not db.query(RoleClosure).filter(
            RoleClosure.ancestor == ADMIN_ROLE_ID,
            RoleClosure.descendant == ADMIN_ROLE_ID,
        ).first():
            db.add(RoleClosure(ancestor=ADMIN_ROLE_ID, descendant=ADMIN_ROLE_ID, depth=0))
            logger.info("创建角色层级关系")

        # 3. 创建超级管理员用户
        if not db.query(User).filter(User.entity_id == ADMIN_ROLE_ID).first():
            db.add(
                User(
                    entity_id=ADMIN_ROLE_ID,
                    username=ADMIN_USERNAME,
                    name=ADMIN_NAME,
                    mobile=ADMIN_MOBILE,
                    password_hash=hash_password(ADMIN_PASSWORD),
                    gender=ADMIN_GENDER,
                    email=ADMIN_EMAIL,
                    status=1,
                    nick_name=ADMIN_NICK_NAME,
                )
            )
            logger.info("创建超级管理员用户")

        # 4. 创建用户角色关联
        if not db.query(UserRoleRelations).filter(
            UserRoleRelations.user_id == ADMIN_ROLE_ID,
            UserRoleRelations.role_id == ADMIN_ROLE_ID,
        ).first():
            db.add(UserRoleRelations(user_id=ADMIN_ROLE_ID, role_id=ADMIN_ROLE_ID))
            logger.info("创建用户角色关联")

        db.commit()
        logger.info("超级管理员用户初始化完成，用户名: {}", ADMIN_USERNAME)
        logger.warning("请在生产环境中立即修改默认凭据和个人信息")
        return True

    except IntegrityError as exc:
        db.rollback()
        if "Duplicate entry" in str(exc):
            logger.warning("管理员数据已存在，跳过初始化")
            return True
        logger.error(f"数据完整性错误: {exc}")
        return False
    except Exception:
        db.rollback()
        logger.exception("初始化管理员用户失败")
        return False
    finally:
        database.session_maker_local.remove()


def main() -> int:
    """数据库初始化脚本入口。"""
    try:
        logger.info("FastBrace - 数据库初始化")
        logger.info(f"环境: {os.getenv('ENV')}")
        logger.info(f"数据库: {app_settings.db.database}")
        logger.info(f"主机: {app_settings.db.host}:{app_settings.db.port}")

        # 1. 创建数据库（如果不存在）
        create_database_if_not_exists()

        # 2. 加载所有模型
        load_all_models()

        # 3. 初始化数据库连接池
        engine = database.init_database(app_settings.db)

        # 4. 创建缺失表。当前框架迁移链不是完整空库基线，空库应先按模型建表。
        create_model_tables(engine)

        # 5. 数据库迁移。空库建表后直接标记为最新版本；已有版本表则执行增量迁移。
        if has_alembic_version(engine):
            if not run_migrations():
                return 1
        else:
            logger.info("未发现 Alembic 版本表，标记当前模型结构为 head")
            command.stamp(get_alembic_config(), "head")

        # 6. 检查表结构
        if not check_tables():
            return 1

        # 7. 初始化管理员用户
        if not init_admin_user():
            return 1

        logger.info("数据库初始化完成")
        return 0

    except Exception:
        logger.exception("数据库初始化失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
