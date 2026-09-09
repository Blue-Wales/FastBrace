#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : template_render.py
@Author  : Blue-Wales
@Date    : 2026-08-22
"""

import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from loguru import logger


def find_project_root(marker_files: list[str] | None = None) -> Path:
    """查找项目根目录（基于标识文件）

    :param marker_files: 标识文件列表，用于识别项目根目录

    :return 项目根目录的Path对象
    """
    if marker_files is None:
        # 常见的项目根目录标识文件
        marker_files = [
            "main.py",  # 启动文件
            "pyproject.toml",  # Python项目配置
            "requirements.txt",  # 依赖文件
            "README.md",  # 说明文件
        ]

    # 从当前文件开始向上查找
    current_path = Path(__file__).resolve().parent

    while current_path != current_path.parent:  # 避免到达根目录
        # 检查是否存在任何标识文件
        for marker in marker_files:
            marker_path = current_path / marker
            if marker_path.exists():
                logger.debug(f"找到项目根目录: {current_path} (基于标识文件: {marker})")
                return current_path

        # 向上一级目录查找
        current_path = current_path.parent

    # 如果找不到，抛出异常
    raise FileNotFoundError(
        f"找不到项目根目录！请确保项目根目录包含以下任一文件: {', '.join(marker_files)}"
    )


def get_templates_dir_path(
    template_subdir: str = "templates", fallback_to_relative: bool = True
) -> Path:
    """获取模板目录路径（多种策略）

    :param template_subdir: 模板子目录名称
    :param fallback_to_relative: 如果找不到项目根目录，是否回退到相对路径

    :return 模板目录的绝对路径
    """
    # 策略1: 环境变量指定
    env_templates_dir = os.getenv("TEMPLATES_DIR")
    if env_templates_dir:
        templates_path = Path(env_templates_dir)
        if templates_path.exists():
            logger.info(f"使用环境变量指定的模板目录: {templates_path}")
            return templates_path.resolve()
        logger.warning(f"环境变量TEMPLATES_DIR指定的目录不存在: {env_templates_dir}")

    # 策略2: 项目根目录 + templates子目录
    try:
        project_root = find_project_root()
        templates_path = project_root / template_subdir

        logger.info(f"使用项目根目录下的模板目录: {templates_path}")
        return templates_path.resolve()

    except FileNotFoundError as e:
        logger.warning(f"无法找到项目根目录: {e}")

        if not fallback_to_relative:
            raise

    # 策略3: 回退到相对路径（当前工作目录 + templates）
    cwd_templates = Path.cwd() / template_subdir

    logger.warning(f"回退到当前工作目录下的模板目录: {cwd_templates}")
    return cwd_templates.resolve()


class TemplateRender:
    """模板管理器 - 支持Jinja2模板引擎，可靠地处理模板路径"""

    def __init__(self, topic: str, template_dir: str | Path | None = None):
        """
        初始化模板管理器

        :param topic: 模板主题
        :param template_dir: 模板目录路径
            - None: 自动查找项目根目录下的templates目录
            - str/Path: 指定的模板目录路径
        """
        if template_dir is None:
            # 自动查找项目根目录下的templates目录
            self.template_dir = get_templates_dir_path()
        else:
            # 使用指定的目录
            self.template_dir = Path(template_dir).resolve()

        self.template_dir = self.template_dir / topic

        # 不在初始化时创建目录，延迟到实际使用时创建，避免容器非root用户启动时权限报错
        self._env: Environment | None = None

        logger.info(f"模板管理器初始化完成，模板目录: {self.template_dir}")

    def _ensure_dir_and_env(self) -> None:
        """确保模板目录存在并初始化 Jinja2 环境（懒加载）"""
        if self._env is not None:
            return
        if not self.template_dir.exists():
            self.template_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建模板目录: {self.template_dir}")
        self._env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        )

    @property
    def env(self) -> Environment:
        self._ensure_dir_and_env()
        return self._env

    def render_template(self, template_name: str, **context) -> str:
        """渲染模板

        :param template_name: 模板文件名 (例如: 'welcome.txt', 'reset_password.html')
        :param context: 模板变量
        :return 渲染后的内容
        """
        template = self.env.get_template(template_name)
        content = template.render(**context)
        logger.debug(f"模板渲染成功: {template_name}")
        return content

    def get_template_list(self) -> list[str]:
        """获取所有可用的模板文件列表"""
        templates = []
        if self.template_dir.exists():
            # 支持多种文件类型
            for pattern in ["*.txt", "*.html", "*.xml", "*.json"]:
                for file in self.template_dir.glob(pattern):
                    templates.append(file.name)
        return sorted(templates)

    def template_exists(self, template_name: str) -> bool:
        """检查模板文件是否存在"""
        template_path = self.template_dir / template_name
        return template_path.exists()

    def create_template_from_string(self, template_name: str, content: str) -> None:
        """从字符串创建模板文件"""
        template_path = self.template_dir / template_name
        template_path.write_text(content, encoding="utf-8")
        logger.info(f"模板文件已创建: {template_path}")

    def get_template_path(self, template_name: str) -> Path:
        """获取模板文件的完整路径"""
        return self.template_dir / template_name

    def reload_templates(self) -> None:
        """重新加载模板（清除缓存）"""
        # 重置懒加载环境，下次访问时重新初始化
        self._env = None
        logger.info("模板缓存已清除，重新加载")
