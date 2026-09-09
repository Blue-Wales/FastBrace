#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : user_repo.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 用户仓储实现
"""

import builtins
from collections import defaultdict
from functools import partial
from typing import Any

from sqlalchemy import and_, func, select

from domain.entity.user import UserEntity
from domain.repo.base import BaseRepository
from domain.value_object.user_vo import UserInfoVO, UserMobileVO, UserSummaryVO
from infrastructure.core.container import repository_factory
from infrastructure.core.enum_var import BeanScope
from infrastructure.core.error_handler import NotFoundError
from infrastructure.models.user import User, UserRoleRelations


def save_origin_entity_id(
    user_entity: UserEntity,
    exist_users_dict: dict | None = None,
    include_columns: list[str] | None = None,
) -> dict[str, Any]:
    """批量导入时复用已有用户 ID 并裁剪模型字段。"""
    if exist_users_dict and user_entity.username in exist_users_dict:
        user_entity.entity_id = exist_users_dict[user_entity.username]
    include_set = set(include_columns) if include_columns else None
    return user_entity.model_dump(include=include_set)


@repository_factory.autowire("user_repo", scope=BeanScope.PROTOTYPE.value)
class UserRepository(BaseRepository):
    """基于 SQLAlchemy 的用户仓储实现。"""

    async def get_by_id(self, user_id: int | str, id_type="entity_id") -> UserEntity:
        """按调用方指定的模型字段查询用户。"""
        user_obj = self.db.query(User).filter(getattr(User, id_type) == user_id).first()
        if not user_obj:
            raise NotFoundError("用户不存在")
        return self._to_entity(user_obj, UserEntity)

    async def get_by_username(self, username: str) -> UserEntity | None:
        """按唯一用户名查询并转换用户实体。"""
        user_obj = self.db.query(User).filter(User.username == username).first()
        if not user_obj:
            return None
        return self._to_entity(user_obj, UserEntity)

    async def add(self, user_entity: UserEntity):
        """将用户实体转换为 ORM 模型后加入会话。"""
        self.db.add(self._to_model(User, user_entity))

    async def delete(self, user_id: int) -> int:
        """删除用户"""
        return self.db.query(User).filter(User.entity_id == user_id).delete()

    async def batch_add(self, user_entity_list: list[UserEntity]):
        """复用已有 ID 后批量 upsert 用户。"""
        exist_users_list = self.db.query(User.username, User.entity_id).all()
        exist_users_dict = {row[0]: row[1] for row in exist_users_list}
        include_columns = [column.name for column in User.__table__.columns]
        user_data_list = list(
            map(
                partial(
                    save_origin_entity_id,
                    exist_users_dict=exist_users_dict,
                    include_columns=include_columns,
                ),
                user_entity_list,
            )
        )
        self.batch_upsert(User, user_data_list, ["username", "entity_id"])
        return True

    async def list(
        self,
        page: int | None = None,
        page_size: int | None = None,
        name: str | None = None,
        nick_name: str | None = None,
        mobile: str | None = None,
        user_id_list: list[int] | None = None,
        status: bool | None = None,
        excluded: bool = False,
    ) -> tuple[list[UserEntity], int]:
        """组合筛选条件并按需执行分页查询。"""
        query = self.db.query(User).order_by(User.entity_id.desc())
        total = 0
        if status is not None:
            query = query.filter(User.status == status)
        if name is not None:
            query = query.filter(User.name.like(f"%{name}%"))
        if nick_name is not None:
            query = query.filter(User.nick_name.like(f"%{nick_name}%"))
        if mobile is not None:
            query = query.filter(User.mobile.like(f"%{mobile}%"))
        if user_id_list and excluded:
            query = query.filter(~User.entity_id.in_(user_id_list))
        elif user_id_list:
            query = query.filter(User.entity_id.in_(user_id_list))
        if page is not None and page_size is not None:
            total = query.with_entities(func.count(User.id)).scalar()
            query = query.offset((page - 1) * page_size).limit(page_size)
        result = query.all()
        return [self._to_entity(user_obj, UserEntity) for user_obj in result], total

    async def user_role_relations(
        self, user_ids: builtins.list[int]
    ) -> dict[int, builtins.list[int]]:
        """查询并聚合用户到角色 ID 的映射。"""
        relations = self.db.query(UserRoleRelations).filter(UserRoleRelations.user_id.in_(user_ids))
        user_role_map = defaultdict(list)
        for relation in relations:
            user_role_map[relation.user_id].append(relation.role_id)
        return user_role_map

    async def has_role(self, user_id: int, role_id: int) -> bool:
        """通过关联记录是否存在判断用户角色关系。"""
        relations = (
            self.db.query(UserRoleRelations)
            .filter(UserRoleRelations.user_id == user_id, UserRoleRelations.role_id == role_id)
            .first()
        )
        return relations is not None

    async def save(self, user_entity: UserEntity):
        """裁剪为表字段后更新非空用户属性。"""
        update_data = user_entity.model_dump(
            include={c.name for c in User.__table__.columns},
            exclude={"entity_id"},
            exclude_none=True,
        )
        return (
            self.db.query(User).filter(User.entity_id == user_entity.entity_id).update(update_data)
        )

    async def change_status(
        self, user_id_list: builtins.list[int], status: bool, current_user_name: str
    ) -> int:
        """变更用户状态"""
        return (
            self.db.query(User)
            .filter(User.entity_id.in_(user_id_list))
            .update({"status": status, "last_operator": current_user_name})
        )

    async def update_related_roles(self, user_id: int, role_ids: builtins.list[int]):
        """删除旧关联后重建用户角色关系。"""
        # 先删除用户关联的角色
        delete_result = (
            self.db.query(UserRoleRelations).filter(UserRoleRelations.user_id == user_id).delete()
        )
        user_role_list = [
            UserRoleRelations(user_id=user_id, role_id=role_id) for role_id in role_ids
        ]
        # 再重新添加用户关联的角色
        if len(user_role_list) != 0:
            self.db.add_all(user_role_list)
        # 返回删除结果
        return delete_result

    async def name_list(self, name=None, status=True):
        """投影用户 ID 和名称并应用状态、名称筛选。"""
        query = self.db.query(User.entity_id, User.name).filter(User.status == status)
        if name is not None:
            query = query.filter(User.name.like(f"%{name}%"))
        result = query.all()
        return [{"user_id": str(entity_id), "name": name} for entity_id, name in result]

    async def get_default_role_id(self, user_id: int) -> int:
        """沿用关联查询顺序选取首个角色。"""
        user_role_info = await self.user_role_relations(user_ids=[user_id])
        role_ids = user_role_info.get(user_id)
        if not role_ids:
            raise PermissionError("用户没有角色")
        return role_ids[0]

    async def get_summary_info(self, entity_id: int):
        """投影启用用户的摘要字段。"""
        stmt = select(User.entity_id, User.name).where(
            User.entity_id == entity_id, User.status == 1
        )

        result = self.db.execute(stmt).first()

        if result is None:
            raise NotFoundError(message=f"顾问不存在，或者已禁用: id={entity_id}")

        return self._to_entity(result, UserSummaryVO)

    async def get_user_mobile_by_id(self, entity_id: int):
        """投影启用用户的手机号信息。"""
        stmt = select(User.entity_id, User.name, User.mobile).where(
            User.entity_id == entity_id, User.status == 1
        )

        result = self.db.execute(stmt).first()

        if result is None:
            raise NotFoundError(message=f"顾问不存在，或者已禁用: id={entity_id}")

        return self._to_entity(result, UserMobileVO)

    async def get_user_by_mobile(self, mobile: str):
        """按手机号投影未删除用户的顾问信息。"""
        query = select(
            User.entity_id,
            User.name,
            User.gender,
            User.nick_name,
            User.personal_profile,
            User.personal_advantage,
            User.wecom_number,
        ).where(and_(User.mobile == mobile, User.status != 2))
        result = self.db.execute(query)
        row = result.first()
        if row is None:
            return None
        return self._to_entity(row, UserInfoVO)

    async def get_all_normal_users(self):
        """投影全部未删除用户 ID。"""
        query = select(User.entity_id).where(User.status != 2)
        result = self.db.execute(query)
        return result.mappings().all()
