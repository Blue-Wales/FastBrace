#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : permission_init.py
@Author  : Blue-Wales
@Date    : 2026-08-25
@Desc    : 权限资源初始化脚本，在 Docker 部署时初始化权限资源数据

用法:
    python scripts/permission_init.py                   # 已存在权限资源时跳过
    python scripts/permission_init.py --force-recreate  # 强制清空并重建
"""

import argparse
import sys
from pathlib import Path
from typing import Any

# 保证从任意目录运行脚本时都能导入项目内的 infrastructure 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger
from sqlalchemy import URL, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker

from infrastructure.core.enum_var import PermissionLevel, Permissions
from infrastructure.core.settings import app_settings
from infrastructure.models.permission_resources import PermissionResources
from infrastructure.models.role import ADMIN_ROLE_CODE, ADMIN_ROLE_ID, Role
from infrastructure.utils.permission_constants import (
    PERMISSION_ACTION_NAMES,
    PERMISSION_MAPPING,
    PERMISSION_START_ENTITY_ID,
    PERMISSION_START_ID,
)


def _action_name(action: str, module_name: str) -> str:
    """拼接权限操作的中文名称，未知操作回退为原始编码。"""
    return f"{PERMISSION_ACTION_NAMES.get(action, action)}{module_name}"


class PermissionResourceInitializer:
    """根据权限常量配置生成模块与操作的权限资源树，并写入数据库。"""

    def __init__(self) -> None:
        self.session_maker = self._create_session_maker()
        self._next_id = PERMISSION_START_ID
        self._next_entity_id = PERMISSION_START_ENTITY_ID

    @staticmethod
    def _create_session_maker() -> scoped_session:
        """创建独立的数据库会话工厂，不依赖应用已初始化的连接池。"""
        db_url = URL.create(
            drivername=app_settings.db.drivername,
            username=app_settings.db.username,
            password=app_settings.db.password,
            host=app_settings.db.host,
            port=app_settings.db.port,
            database=app_settings.db.database,
        )
        engine = create_engine(
            db_url,
            pool_size=15,
            max_overflow=5,
            pool_recycle=3600,
            pool_pre_ping=True,
        )
        return scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    def _allocate_ids(self) -> tuple[int, int]:
        """分配一对自增的权限资源 ID 与实体 ID。"""
        resource_id, entity_id = self._next_id, self._next_entity_id
        self._next_id += 1
        self._next_entity_id += 1
        return resource_id, entity_id

    def build_resources(self) -> list[dict[str, Any]]:
        """递归生成权限资源记录，顺序为：模块 -> 操作 -> 子模块。"""
        resources: list[dict[str, Any]] = []

        def process(module: dict[str, Any], parent_id: int | None, depth: int) -> None:
            module_id, module_entity_id = self._allocate_ids()
            resources.append(
                {
                    "id": module_id,
                    "entity_id": module_entity_id,
                    "code": module["code"],
                    "name": module["name"],
                    "description": module["description"],
                    "resource_type": "module",
                    "parent_id": parent_id,
                    "depth": depth,
                    "level": 1,
                }
            )

            for level, actions in module["permission_map"].items():
                for action in actions:
                    action_id, action_entity_id = self._allocate_ids()
                    resources.append(
                        {
                            "id": action_id,
                            "entity_id": action_entity_id,
                            "code": f"{module['code']}:{action}",
                            "name": _action_name(action, module["name"]),
                            "description": _action_name(action, module["name"]),
                            "resource_type": "action",
                            "parent_id": module_entity_id,
                            "depth": depth + 1,
                            "level": level,
                        }
                    )

            for child in module.get("children", []):
                process(child, module_entity_id, depth + 1)

        for module in PERMISSION_MAPPING:
            process(module, None, 1)

        return resources

    def clear_existing_permissions(self) -> None:
        """清空现有权限资源数据。"""
        with self.session_maker() as session:
            try:
                session.query(PermissionResources).delete()
                session.commit()
                logger.info("已清空现有权限资源数据")
            except Exception:
                session.rollback()
                logger.exception("清空权限资源数据失败")
                raise

    def insert_permission_resources(self, resources: list[dict[str, Any]]) -> None:
        """批量插入权限资源数据，重复数据时跳过。"""
        with self.session_maker() as session:
            try:
                for resource in resources:
                    session.add(PermissionResources(**resource))
                session.commit()
                logger.info(f"成功插入 {len(resources)} 条权限资源记录")
            except IntegrityError as exc:
                session.rollback()
                logger.warning(f"权限资源可能已存在，跳过插入: {exc}")
            except Exception:
                session.rollback()
                logger.exception("插入权限资源数据失败")
                raise

    def check_permission_resources(self) -> bool:
        """检查权限资源表是否已有数据。"""
        with self.session_maker() as session:
            try:
                count = session.query(PermissionResources).count()
            except Exception:
                logger.exception("检查权限资源失败")
                return False

        if count:
            logger.info(f"当前权限资源数量: {count}")
        else:
            logger.info("权限资源表为空")
        return count > 0

    def update_admin_permission(self) -> None:
        """为超级管理员角色补齐全部权限。"""
        with self.session_maker() as session:
            admin_role = session.query(Role).filter(Role.entity_id == ADMIN_ROLE_ID).first()
            if admin_role:
                admin_role.code = admin_role.code or ADMIN_ROLE_CODE
                admin_role.permissions = {
                    permission.value: [
                        PermissionLevel.VIEW.value,
                        PermissionLevel.EDIT.value,
                        PermissionLevel.EXPORT.value,
                    ]
                    for permission in Permissions
                }
                session.commit()

    def initialize_permissions(self, force_recreate: bool = False) -> bool:
        """初始化权限资源；已存在时跳过，除非强制重建。"""
        try:
            if not force_recreate and self.check_permission_resources():
                logger.info("权限资源已存在，跳过初始化")
                return True

            if force_recreate:
                self.clear_existing_permissions()

            resources = self.build_resources()
            logger.info(f"生成 {len(resources)} 条权限资源记录")

            self.insert_permission_resources(resources)

            if self.check_permission_resources():
                self.update_admin_permission()
                logger.info("权限资源初始化完成")
                return True

            logger.error("权限资源初始化验证失败")
            return False
        except Exception:
            logger.exception("权限资源初始化失败")
            return False


def main() -> int:
    """权限资源初始化脚本入口。"""
    parser = argparse.ArgumentParser(description="初始化权限资源数据")
    parser.add_argument("--force-recreate", action="store_true", help="强制清空并重建权限资源")
    args = parser.parse_args()

    initializer = PermissionResourceInitializer()
    success = initializer.initialize_permissions(force_recreate=args.force_recreate)
    logger.info("权限资源初始化成功" if success else "权限资源初始化失败")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
