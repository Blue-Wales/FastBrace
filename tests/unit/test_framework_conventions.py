#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : test_framework_conventions.py
@Author  : zhouguangming
@Date    : 2026/07/29 00:00
@Desc    : 脚手架目录与品牌约定测试
"""

import ast
from pathlib import Path

import yaml

from domain.repo.interfaces.user import IUserRepository
from domain.repo.user_repo import UserRepository
from domain.service.interfaces.permission import IPermissionService
from domain.service.permission_service import PermissionService

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTERFACE_DIRS = (
    PROJECT_ROOT / "domain" / "repo" / "interfaces",
    PROJECT_ROOT / "domain" / "service" / "interfaces",
)


def test_domain_interfaces_are_separate_from_implementations():
    assert IUserRepository.__module__ == "domain.repo.interfaces.user"
    assert UserRepository.__module__ == "domain.repo.user_repo"
    assert IPermissionService.__module__ == "domain.service.interfaces.permission"
    assert PermissionService.__module__ == "domain.service.permission_service"


def test_domain_interface_contracts_have_docstrings():
    """领域接口必须在定义处提供模块、类型和公开方法契约。"""
    for interface_dir in INTERFACE_DIRS:
        for interface_path in interface_dir.glob("*.py"):
            module = ast.parse(interface_path.read_text(encoding="utf-8"))
            assert ast.get_docstring(module), f"{interface_path} 缺少模块说明"

            for class_node in (node for node in module.body if isinstance(node, ast.ClassDef)):
                assert ast.get_docstring(class_node), (
                    f"{interface_path}:{class_node.name} 缺少接口说明"
                )
                public_methods = (
                    node
                    for node in class_node.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and not node.name.startswith("_")
                )
                for method_node in public_methods:
                    assert ast.get_docstring(method_node), (
                        f"{interface_path}:{class_node.name}.{method_node.name} 缺少契约说明"
                    )


def test_deployment_files_are_centralized():
    deploy_dir = PROJECT_ROOT / "deploy"

    assert (deploy_dir / "Dockerfile").is_file()
    assert (deploy_dir / "Dockerfile.dockerignore").is_file()
    assert (deploy_dir / "docker-compose.yml").is_file()
    assert (deploy_dir / "deploy.sh").is_file()
    assert not (PROJECT_ROOT / "docker-compose.yml").exists()
    assert not (PROJECT_ROOT / "scripts" / "Dockerfile").exists()


def test_development_settings_use_FastBrace_brand():
    settings_path = PROJECT_ROOT / "infrastructure" / "config" / "settings.dev.yaml"
    settings = yaml.safe_load(settings_path.read_text(encoding="utf-8"))

    assert settings["service_name"] == "FastBrace"
    assert settings["email"]["sender_name"] == "FastBrace"
    assert settings["event_bus"]["name"] == "FastBrace"
