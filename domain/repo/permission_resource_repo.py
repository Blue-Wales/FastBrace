#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : permission_resource_repo.py
@Author  : bright
@Date    : 2026-08-22
@Desc    : 权限资源仓储类
"""

from collections import defaultdict

from loguru import logger

from domain.entity.permission_resource import (
    DetailedPermissionNode,
    PermissionResourceEntity,
    PermissionTreeNode,
)
from domain.repo.base import BaseRepository
from infrastructure.core.container import repository_factory
from infrastructure.core.enum_var import BeanScope
from infrastructure.models.permission_resources import PermissionResources


@repository_factory.autowire("permission_resource_repo", scope=BeanScope.PROTOTYPE.value)
class PermissionResourceRepository(BaseRepository):
    """权限资源仓储"""

    async def get_all_resources(self) -> list[PermissionResourceEntity]:
        """获取所有权限资源"""
        resources = self.db.query(PermissionResources).all()
        return [self._to_entity(resource, PermissionResourceEntity) for resource in resources]

    async def get_modules_only(self) -> list[PermissionResourceEntity]:
        """获取所有模块类型的权限资源"""
        resources = (
            self.db.query(PermissionResources)
            .filter(PermissionResources.resource_type == "module")
            .all()
        )
        return [self._to_entity(resource, PermissionResourceEntity) for resource in resources]

    async def get_actions_only(self) -> list[PermissionResourceEntity]:
        """获取所有动作类型的权限资源"""
        resources = (
            self.db.query(PermissionResources)
            .filter(PermissionResources.resource_type == "action")
            .all()
        )
        return [self._to_entity(resource, PermissionResourceEntity) for resource in resources]

    async def get_by_type_and_parent(
        self, resource_type: str, parent_id: int | None = None
    ) -> list[PermissionResourceEntity]:
        """根据类型和父ID获取权限资源"""
        query = self.db.query(PermissionResources).filter(
            PermissionResources.resource_type == resource_type
        )

        if parent_id is not None:
            query = query.filter(PermissionResources.parent_id == parent_id)
        else:
            query = query.filter(PermissionResources.parent_id.is_(None))

        resources = query.all()
        return [self._to_entity(resource, PermissionResourceEntity) for resource in resources]

    async def build_module_tree(self) -> list[PermissionTreeNode]:
        """构建模块权限树，用于创建角色时选择权限"""
        modules = await self.get_modules_only()

        # 构建父子关系映射
        children_map = defaultdict(list)
        node_map = {}

        for module in modules:
            # 创建权限树节点
            node = PermissionTreeNode(
                entity_id=module.entity_id,
                name=module.name,
                code=module.code,
                description=module.description,
                resource_type=module.resource_type,
                parent_id=module.parent_id,
                depth=module.depth,
                level=module.level,
                available_levels=self._get_available_levels(module.depth),
                selected_levels=[],
                children=[],
            )

            node_map[module.entity_id] = node

            if module.parent_id:
                children_map[module.parent_id].append(node)

        # 构建树结构
        for parent_id, children in children_map.items():
            if parent_id in node_map:
                node_map[parent_id].children = children

        # 返回根节点
        return [node for node in node_map.values() if node.parent_id is None]

    def _get_available_levels(self, depth: int) -> list[int]:
        """根据深度获取可用的权限级别"""
        if depth == 1:
            return [1]  # depth=1的module只开放level 1的可选项
        if depth == 2:
            return [1, 2, 3]  # depth=2的module开放level 1 2 3三个可选项
        return [1, 2, 3]  # 默认开放所有级别

    async def convert_coarse_to_detailed_permissions(
        self,
        coarse_permissions: dict[str, list[int]],
        filter_by_permission: bool = False,
    ) -> list[DetailedPermissionNode]:
        """将粗粒度权限转换为细粒度权限树"""
        # 获取所有权限资源
        all_resources = await self.get_all_resources()

        # 构建code到实体的映射
        code_to_entity = {resource.code: resource for resource in all_resources}

        # 构建父子关系映射
        children_map = defaultdict(list)
        node_map = {}

        for resource in all_resources:
            # 判断权限级别
            permission_level = 0
            has_permission = False

            if resource.resource_type == "module":
                # 模块类型：检查粗粒度权限
                if resource.code in coarse_permissions:
                    has_permission = True
                    permission_level = max(coarse_permissions[resource.code])
            else:
                # 动作类型：根据父模块的权限推断
                parent_code = self._get_parent_module_code(resource, code_to_entity)
                if parent_code and parent_code in coarse_permissions:
                    # 检查该动作需要的权限级别是否被包含
                    required_level = resource.level
                    if required_level in coarse_permissions[parent_code]:
                        has_permission = True
                        permission_level = required_level

            # 如果需要过滤且当前节点没有权限，跳过
            if filter_by_permission and not has_permission:
                continue

            # 创建详细权限节点
            node = DetailedPermissionNode(
                entity_id=resource.entity_id,
                name=resource.name,
                code=resource.code,
                description=resource.description,
                resource_type=resource.resource_type,
                parent_id=resource.parent_id,
                depth=resource.depth,
                level=resource.level,
                permission_level=permission_level,
                children=[],
                action=[],
            )

            node_map[resource.entity_id] = node

            if resource.parent_id:
                children_map[resource.parent_id].append(node)

        if filter_by_permission:
            self._ensure_parent_nodes_exist(
                node_map,
                children_map,
                all_resources,
                coarse_permissions,
                code_to_entity,
            )

        # 构建树结构 - 根据子节点类型决定放入父节点的哪个字段
        for parent_id, children in children_map.items():
            if parent_id in node_map:
                parent_node = node_map[parent_id]

                # 分类子节点：模块类型的放入children，动作类型的放入action
                child_modules = [child for child in children if child.resource_type == "module"]
                child_actions = [child for child in children if child.resource_type == "action"]

                parent_node.children = child_modules
                parent_node.action = child_actions

        # 返回根节点
        return [node for node in node_map.values() if node.parent_id is None]

    def _ensure_parent_nodes_exist(
        self,
        node_map: dict[int, DetailedPermissionNode],
        children_map: defaultdict,
        all_resources: list[PermissionResourceEntity],
        coarse_permissions: dict[str, list[int]],
        code_to_entity: dict[str, PermissionResourceEntity],
    ):
        """确保有权限的子节点的父节点存在"""
        # 构建资源ID到资源的映射
        id_to_resource = {resource.entity_id: resource for resource in all_resources}

        # 递归添加缺失的父节点
        def add_missing_parents(node_id: int):
            if node_id in node_map:
                return

            resource = id_to_resource.get(node_id)
            if not resource:
                return

            # 先确保自己的父节点存在
            if resource.parent_id:
                add_missing_parents(resource.parent_id)

            # 判断当前节点权限级别
            permission_level = 0

            if resource.resource_type == "module":
                if resource.code in coarse_permissions:
                    permission_level = max(coarse_permissions[resource.code])
            else:
                parent_code = self._get_parent_module_code(resource, code_to_entity)
                if parent_code and parent_code in coarse_permissions:
                    required_level = resource.level
                    if required_level in coarse_permissions[parent_code]:
                        permission_level = required_level

            # 创建节点
            node = DetailedPermissionNode(
                entity_id=resource.entity_id,
                name=resource.name,
                code=resource.code,
                description=resource.description,
                resource_type=resource.resource_type,
                parent_id=resource.parent_id,
                depth=resource.depth,
                level=resource.level,
                permission_level=permission_level,
                children=[],
                action=[],
            )

            node_map[resource.entity_id] = node

            if resource.parent_id:
                children_map[resource.parent_id].append(node)

        # 收集所有需要的父节点ID并递归添加
        needed_parent_ids = set()
        for node in list(node_map.values()):
            if node.parent_id:
                needed_parent_ids.add(node.parent_id)

        for parent_id in needed_parent_ids:
            add_missing_parents(parent_id)

    def _get_parent_module_code(
        self,
        resource: PermissionResourceEntity,
        code_to_entity: dict[str, PermissionResourceEntity],
    ) -> str | None:
        """获取父模块的code"""
        if resource.parent_id is None:
            return None

        # 查找父资源
        parent = next(
            (r for r in code_to_entity.values() if r.entity_id == resource.parent_id),
            None,
        )
        if parent is None:
            return None

        # 如果父资源是模块，返回其code
        if parent.resource_type == "module":
            return parent.code

        # 如果父资源不是模块，递归查找
        return self._get_parent_module_code(parent, code_to_entity)

    async def get_actions_by_module_and_level(
        self, module_code: str, level: int
    ) -> list[PermissionResourceEntity]:
        """根据模块和级别获取对应的动作权限"""
        # 先获取模块
        module = (
            self.db.query(PermissionResources)
            .filter(
                PermissionResources.code == module_code,
                PermissionResources.resource_type == "module",
            )
            .first()
        )

        if not module:
            return []

        # 获取该模块下指定级别的所有动作
        actions = (
            self.db.query(PermissionResources)
            .filter(
                PermissionResources.parent_id == module.entity_id,
                PermissionResources.resource_type == "action",
                PermissionResources.level == level,
            )
            .all()
        )

        return [self._to_entity(action, PermissionResourceEntity) for action in actions]

    async def validate_module_permissions(self, permissions: dict[str, list[int]]) -> bool:
        """验证模块权限的有效性"""
        modules = await self.get_modules_only()
        module_codes = {module.code for module in modules}

        for module_code, levels in permissions.items():
            # 检查模块是否存在
            if module_code not in module_codes:
                logger.warning(f"未知模块代码: {module_code}")
                return False

            # 检查权限级别是否有效
            for level in levels:
                if level not in [1, 2, 3]:
                    logger.warning(f"无效的权限级别: {level}")
                    return False

        return True
