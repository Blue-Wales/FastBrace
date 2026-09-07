#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : permission_constants.py
@Author  : bright
@Date    : 2026-08-25
@Desc    : 权限资源初始化常量配置
"""

from typing import Any

# 权限资源起始 ID：与历史数据错开，实体 ID 使用独立的大整数段
PERMISSION_START_ID = 104
PERMISSION_START_ENTITY_ID = 1000000

# 权限操作编码 -> 中文名称，用于拼接权限资源名称
PERMISSION_ACTION_NAMES: dict[str, str] = {
    "View": "查看",
    "Add": "新增",
    "Edit": "编辑",
    "Delete": "删除",
    "Export": "导出",
    "Import": "导入",
    "ChangeStatus": "修改状态",
    "ChangePassword": "修改密码",
    "AddTags": "批量添加标签到",
    "Sync": "同步",
    "Bind": "绑定",
    "Update": "更新",
    "AddUsers": "批量添加用户到",
}

# 权限资源树配置。
# permission_map 的 key 对应 PermissionLevel 编码（1 查看 / 2 操作 / 3 导出），
# value 为该级别下需要生成的权限操作编码列表。
PERMISSION_MAPPING: list[dict[str, Any]] = [
    {
        "code": "Dashboard",
        "name": "仪表盘",
        "description": "仪表盘模块",
        "permission_map": {1: ["View"], 2: [], 3: []},
        "children": [],
    },
    {
        "code": "UserManage",
        "name": "用户管理",
        "description": "用户管理模块",
        "permission_map": {1: ["View"], 2: [], 3: []},
        "children": [
            {
                "code": "UserManage.Account",
                "name": "账户",
                "description": "账户模块",
                "permission_map": {
                    1: ["View"],
                    2: ["Add", "Edit", "Delete", "ChangeStatus", "ChangePassword"],
                    3: [],
                },
            },
            {
                "code": "UserManage.Role",
                "name": "角色",
                "description": "角色模块",
                "permission_map": {
                    1: ["View"],
                    2: ["Add", "Edit", "Delete", "AddUsers"],
                    3: [],
                },
            },
            {
                "code": "UserManage.Department",
                "name": "部门",
                "description": "部门模块",
                "permission_map": {
                    1: ["View"],
                    2: ["Add", "Edit", "Delete", "AddUsers"],
                    3: [],
                },
            }
        ],
    },
]
