#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : permission_service.py
@Author  : Blue-Wales
@Date    : 2026-08-22
@Desc    : 权限服务类
"""

from loguru import logger

from domain.entity.permission_resource import DetailedPermissionNode, PermissionTreeNode
from domain.repo.interfaces.permission_resource import IPermissionResourceRepository
from domain.repo.interfaces.role import IRoleRepository
from infrastructure.core.container import domain_service_factory
from infrastructure.core.enum_var import BeanScope


@domain_service_factory.autowire("permission_service", scope=BeanScope.PROTOTYPE.value)
class PermissionService:
    """权限服务"""

    def __init__(self, permission_repo: IPermissionResourceRepository, role_repo: IRoleRepository):
        self.permission_repo = permission_repo
        self.role_repo = role_repo

    async def get_permission_tree_for_role_creation(self) -> list[PermissionTreeNode]:
        """获取用于创建角色的权限树"""
        try:
            return await self.permission_repo.build_module_tree()
        except Exception as e:
            logger.error(f"构建权限树失败: {e}")
            raise

    async def get_role_permission_tree(self, role_id: int) -> list[PermissionTreeNode]:
        """获取角色的权限树（带选中状态）"""
        try:
            # 获取角色信息
            role = await self.role_repo.get_by_id(role_id)
            if not role:
                logger.warning(f"角色 {role_id} 不存在")
                return []

            # 获取权限树
            tree = await self.permission_repo.build_module_tree()

            # 设置选中状态
            self._set_selected_permissions(tree, role.permissions)

            return tree
        except Exception as e:
            logger.error(f"获取角色 {role_id} 的权限树失败: {e}")
            raise

    def _set_selected_permissions(
        self, tree: list[PermissionTreeNode], role_permissions: dict[str, list[int]]
    ):
        """设置权限树的选中状态"""
        for node in tree:
            if node.code in role_permissions:
                node.selected_levels = role_permissions[node.code]

            # 递归处理子节点
            if node.children:
                self._set_selected_permissions(node.children, role_permissions)

    async def save_role_permissions(self, role_id: int, permissions: dict[str, list[int]]) -> bool:
        """保存角色权限"""
        try:
            # 验证权限的有效性
            if not await self.permission_repo.validate_module_permissions(permissions):
                logger.warning(f"角色 {role_id} 的权限无效")
                return False

            # 获取角色实体
            role = await self.role_repo.get_by_id(role_id)
            if not role:
                logger.warning(f"角色 {role_id} 不存在")
                return False

            # 更新权限
            role.permissions = permissions

            # 保存到数据库
            result = await self.role_repo.save(role)

            if result:
                return True
            logger.error(f"保存角色 {role_id} 的权限失败")
            return False

        except Exception as e:
            logger.error(f"保存角色权限失败: {e}")
            return False

    async def get_detailed_permissions_for_frontend(
        self, role_id: int
    ) -> list[DetailedPermissionNode]:
        """获取用于前端的细粒度权限树"""
        try:
            # 获取角色信息
            role = await self.role_repo.get_by_id(role_id)
            if not role:
                logger.warning(f"角色 {role_id} 不存在")
                return []

            # 转换为细粒度权限
            return await self.permission_repo.convert_coarse_to_detailed_permissions(
                role.permissions
            )
        except Exception as e:
            logger.error(f"获取角色 {role_id} 的细粒度权限失败: {e}")
            raise

    async def get_filtered_detailed_permissions_for_frontend(
        self, role_id: int
    ) -> list[DetailedPermissionNode]:
        """获取用于前端的过滤后细粒度权限树（仅包含有权限的节点）"""
        try:
            # 获取角色信息
            role = await self.role_repo.get_by_id(role_id)
            if not role:
                logger.warning(f"角色 {role_id} 不存在")
                return []

            # 转换为细粒度权限，只返回有权限的节点
            return await self.permission_repo.convert_coarse_to_detailed_permissions(
                role.permissions, filter_by_permission=True
            )
        except Exception as e:
            logger.error(f"获取角色 {role_id} 的过滤后细粒度权限失败: {e}")
            raise

    async def get_user_detailed_permissions(
        self, user_permissions: dict[str, list[int]]
    ) -> list[DetailedPermissionNode]:
        """获取用户的细粒度权限（用于前端控制）"""
        try:
            # 转换为细粒度权限
            return await self.permission_repo.convert_coarse_to_detailed_permissions(
                user_permissions
            )
        except Exception as e:
            logger.error(f"获取用户的细粒度权限失败: {e}")
            raise

    async def get_user_filtered_detailed_permissions(
        self, user_permissions: dict[str, list[int]]
    ) -> list[DetailedPermissionNode]:
        """获取用户的过滤后细粒度权限（仅包含有权限的节点）"""
        try:
            # 转换为细粒度权限，只返回有权限的节点
            return await self.permission_repo.convert_coarse_to_detailed_permissions(
                user_permissions, filter_by_permission=True
            )
        except Exception as e:
            logger.error(f"获取用户的过滤后细粒度权限失败: {e}")
            raise

    async def validate_user_permission(
        self,
        user_permissions: dict[str, list[int]],
        module_code: str,
        required_level: int,
    ) -> bool:
        """验证用户是否有指定模块的权限"""
        try:
            if module_code not in user_permissions:
                return False

            return required_level in user_permissions[module_code]
        except Exception as e:
            logger.error(f"验证用户权限失败: {e}")
            return False

    async def get_permission_summary(self, permissions: dict[str, list[int]]) -> dict[str, str]:
        """获取权限摘要（用于显示）"""
        try:
            summary = {}

            for module_code, levels in permissions.items():
                level_names = []
                for level in levels:
                    if level == 1:
                        level_names.append("查看")
                    elif level == 2:
                        level_names.append("操作")
                    elif level == 3:
                        level_names.append("导出")

                summary[module_code] = ", ".join(level_names)

            return summary
        except Exception as e:
            logger.error(f"获取权限摘要失败: {e}")
            return {}

    async def merge_permissions(
        self, permissions_list: list[dict[str, list[int]]]
    ) -> dict[str, list[int]]:
        """合并多个权限集合（取并集）"""
        try:
            merged = {}

            for permissions in permissions_list:
                for module_code, levels in permissions.items():
                    if module_code not in merged:
                        merged[module_code] = []

                    # 合并权限级别，去重
                    merged[module_code] = list(set(merged[module_code] + levels))

            return merged
        except Exception as e:
            logger.error(f"合并权限失败: {e}")
            return {}

    async def get_max_permission_level(
        self, permissions: dict[str, list[int]], module_code: str
    ) -> int:
        """获取用户在指定模块的最大权限级别"""
        try:
            if module_code not in permissions:
                return 0

            return max(permissions[module_code]) if permissions[module_code] else 0
        except Exception as e:
            logger.error(f"获取用户在指定模块的最大权限级别失败: {e}")
            return 0
