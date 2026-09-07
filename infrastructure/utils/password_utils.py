#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : password_utils.py
@Author  : bright
@Date    : 2026-08-22
"""

import random
import string

import bcrypt


def hash_password(password: str) -> str:
    """对密码进行哈希加密

    :param password: 明文密码
    :return: 加密后的密码哈希
    """
    # 生成盐值并加密密码
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配

    :param plain_password: 明文密码
    :param hashed_password: 哈希后的密码
    :return: 密码是否匹配
    """
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def generate_random_password() -> str:
    """生成随机密码

    :return: 随机密码
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=12))
