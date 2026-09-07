#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : swagger_ui_patch.py
@Author  : bright
@Date    : 2026-08-22
"""

import base64
import os

from fastapi.openapi.docs import get_swagger_ui_html

current_dir = os.path.dirname(os.path.abspath(__file__))


# 将 Swagger UI 文件转换为 base64 编码
def get_swagger_ui_bundle():
    # 读取本地 swagger-ui-bundle.js 文件
    file_path = os.path.join(current_dir, "statics", "swagger-ui-bundle.min.js")
    with open(file_path, "rb") as f:
        content = f.read()
    return f"data:text/javascript;base64,{base64.b64encode(content).decode()}"


def get_swagger_ui_css():
    # 读取本地 swagger-ui.css 文件
    file_path = os.path.join(current_dir, "statics", "swagger-ui.min.css")
    with open(file_path, "rb") as f:
        content = f.read()
    return f"data:text/css;base64,{base64.b64encode(content).decode()}"


# 猴子补丁替换资源链接（需在创建FastAPI实例前执行）
def swagger_monkey_patch(*args, **kwargs):
    return get_swagger_ui_html(
        *args,
        **kwargs,
        swagger_js_url=get_swagger_ui_bundle(),
        swagger_css_url=get_swagger_ui_css(),
    )
