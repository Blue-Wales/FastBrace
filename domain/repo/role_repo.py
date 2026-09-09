#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : role_repo.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 角色仓储实现（基于 SQLAlchemy 与闭包表）
"""

from collections import defaultdict
from itertools import chain

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from domain.entity.role import RoleEntity
from domain.repo.base import BaseRepository
from infrastructure.core.container import repository_factory
from infrastructure.core.enum_var import BeanScope
from infrastructure.core.error_handler import DuplicateEntryError, NotFoundError
from infrastructure.models.role import Role, RoleClosure
from infrastructure.models.user import UserRoleRelations


@repository_factory.autowire("role_repo", scope=BeanScope.PROTOTYPE.value)
class RoleRepository(BaseRepository):
    """基于 SQLAlchemy 和闭包表的角色仓储实现。"""

    async def add(self, parent_role_id, role_entity: RoleEntity):
        """写入角色并批量补齐自身及祖先闭包关系。"""
        try:
            role_obj = self._to_model(Role, role_entity)
            role_closure_relations = (
                self.db.query(RoleClosure).filter(RoleClosure.descendant == parent_role_id).all()
            )
            new_role_closure_relations = [
                {"ancestor": role_obj.entity_id, "descendant": role_obj.entity_id, "depth": 0},
            ]
            for role_closure_relation in role_closure_relations:
                new_role_closure_relations.append(
                    {
                        "ancestor": role_closure_relation.ancestor,
                        "descendant": role_obj.entity_id,
                        "depth": role_closure_relation.depth + 1,
                    }
                )
            self.db.add(role_obj)
            self.db.bulk_insert_mappings(RoleClosure, new_role_closure_relations)
        except IntegrityError:
            raise DuplicateEntryError("角色名称或角色编码不可以重复")
        return str(role_obj.entity_id)

    async def get_tree(self, root_id: int = 1):
        """基于直接父子闭包关系迭代构建角色树。"""
        role_relations = (
            self.db.query(RoleClosure)
            .filter(RoleClosure.depth == 1)
            .order_by(RoleClosure.depth.desc())
            .all()
        )
        role_info = self.db.query(Role).all()
        role_info_dict = {role.entity_id: self._to_entity(role, RoleEntity) for role in role_info}
        child_map = defaultdict(list)
        for role_relation in role_relations:
            child_map[role_relation.ancestor].append(role_relation.descendant)

        stack = []
        tree = None

        root_role = role_info_dict.get(root_id)

        if not root_role:
            raise NotFoundError("角色不存在")

        stack.append((root_role, None))

        while stack:
            node, parent = stack.pop()
            # 如果是根节点，则直接加入最终树
            if parent is None and node.entity_id == root_id:
                tree = node

            # 添加当前节点作为其父节点的子节点
            if parent is not None:
                if parent.child_role is None:
                    parent.child_role = []
                parent.child_role.append(node)

            # 如果当前节点有子节点，则将这些子节点按任意顺序（这里选择升序）压入栈中
            for child_id in child_map.get(node.entity_id, []):
                stack.append((role_info_dict[child_id], node))
        return tree

    async def save(self, role_entity: RoleEntity):
        """按实体字段更新角色记录。"""
        update_data = role_entity.model_dump(exclude={"entity_id", "child_role", "related_users"})
        return (
            self.db.query(Role).filter(Role.entity_id == role_entity.entity_id).update(update_data)
        )

    async def user_id_list(self, role_ids: list[int]):
        """查询角色关联用户并去重。"""
        user_id_list = (
            self.db.query(UserRoleRelations.user_id)
            .filter(UserRoleRelations.role_id.in_(role_ids))
            .all()
        )
        return list(set(chain(*user_id_list)))

    async def all_role_map(self):
        """查询并构建角色实体 ID 映射。"""
        role_info = self.db.query(Role).all()
        return {role.entity_id: self._to_entity(role, RoleEntity) for role in role_info}

    async def get_by_id(self, role_id) -> RoleEntity:
        """查询角色并回填关联用户和子角色。"""
        role_info = self.db.query(Role).filter(Role.entity_id == role_id).first()
        if not role_info:
            raise NotFoundError("角色不存在")
        role_entity = self._to_entity(role_info, RoleEntity)
        related_users = (
            self.db.query(UserRoleRelations.user_id)
            .filter(UserRoleRelations.role_id == role_id)
            .all()
        )
        role_entity.related_users = list(chain(*related_users))
        role_tree = await self.get_tree(role_id)
        if role_tree:
            role_entity.child_role = role_tree.child_role
        return role_entity

    async def remove(self, role_id: int):
        """删除角色及其作为后代的闭包关系。"""
        role_result = self.db.query(Role).filter(Role.entity_id == role_id).delete()
        closure_result = (
            self.db.query(RoleClosure).filter(RoleClosure.descendant == role_id).delete()
        )
        return all([role_result, closure_result])

    async def add_users(self, role_id: int, user_ids: list[int]):
        """批量 upsert 角色用户关联。"""
        role_user_dict = [{"role_id": role_id, "user_id": user_id} for user_id in user_ids]
        return self.batch_upsert(
            UserRoleRelations,
            role_user_dict,
            on_duplicate_key_list=["role_id", "user_id"],
        )

    async def remove_users(self, role_id: int, user_ids: list[int]):
        """批量删除角色用户关联。"""
        return (
            self.db.query(UserRoleRelations)
            .filter(
                UserRoleRelations.role_id == role_id,
                UserRoleRelations.user_id.in_(user_ids),
            )
            .delete()
        )

    async def child_role_user_id_list(self, role_id: int, depth: int | None = None):
        """通过闭包表子查询获取后代角色的关联用户。"""
        query = select(RoleClosure.descendant).where(RoleClosure.ancestor == role_id)

        if depth is not None:
            query = query.where(RoleClosure.depth <= depth)
        else:
            query = query.where(RoleClosure.depth > 0)

        subquery = query.subquery()

        user_query = (
            select(UserRoleRelations.user_id)
            .where(UserRoleRelations.role_id.in_(select(subquery.c.descendant)))
            .distinct()
        )

        result = self.db.execute(user_query)
        return result.scalars().all()

    async def ancestor_role_user_id_list(self, role_ids: list[int]):
        """通过闭包表查询祖先角色并复用用户关联查询。"""
        if not role_ids:
            return []
        # 查 ancestor role id 列表
        query = select(RoleClosure.ancestor).where(
            RoleClosure.descendant.in_(role_ids), RoleClosure.depth > 0
        )
        result = self.db.execute(query)
        ancestor_role_ids = list(set(result.scalars().all()))
        if not ancestor_role_ids:
            return []
        # 复用已有方法，获取这些角色对应的 user_id 列表
        return await self.user_id_list(ancestor_role_ids)

    async def get_user_role_names(self, user_id: int) -> list[UserRoleRelations]:
        """查询用户关联的角色 ID 行。"""
        stmt = select(UserRoleRelations.role_id).where(UserRoleRelations.user_id == user_id)
        return self.db.execute(stmt).all()
