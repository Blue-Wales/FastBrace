#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : rsa_utils.py
@Author  : bright
@Date    : 2026-08-22
"""

import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from loguru import logger

from infrastructure.core.error_handler import InvalidInputError
from infrastructure.core.settings import app_settings


class RSAUtils:
    """RSA加密解密工具类"""

    @staticmethod
    def generate_key_pair(key_size: int = 2048) -> tuple[str, str]:
        """生成RSA密钥对

        :param key_size: 密钥长度，默认2048位
        :return: (私钥PEM, 公钥PEM)
        """
        try:
            # 生成私钥
            private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=key_size, backend=default_backend()
            )

            # 序列化私钥
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ).decode("utf-8")

            # 获取公钥并序列化
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode("utf-8")

            return private_pem, public_pem

        except Exception as e:
            logger.error(f"生成RSA密钥对失败: {e}")
            raise

    @staticmethod
    def encrypt_with_public_key(data: str, public_key_pem: str) -> str:
        """使用公钥加密数据

        :param data: 要加密的明文数据
        :param public_key_pem: PEM格式的公钥
        :return: Base64编码的加密数据
        """
        try:
            # 加载公钥
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode("utf-8"), backend=default_backend()
            )

            # 确保是RSA公钥
            if not isinstance(public_key, RSAPublicKey):
                raise ValueError("提供的公钥不是RSA类型")

            # 加密数据
            encrypted_data = public_key.encrypt(
                data.encode("utf-8"),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            # Base64编码
            return base64.b64encode(encrypted_data).decode("utf-8")

        except Exception as e:
            logger.error(f"RSA公钥加密失败: {e}")
            raise

    @staticmethod
    def decrypt_with_private_key(encrypted_data: str, private_key_pem: str) -> str:
        """使用私钥解密数据

        :param encrypted_data: Base64编码的加密数据
        :param private_key_pem: PEM格式的私钥
        :return: 解密后的明文数据
        """
        try:
            # 加载私钥
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode("utf-8"),
                password=None,
                backend=default_backend(),
            )

            # 确保是RSA私钥
            if not isinstance(private_key, RSAPrivateKey):
                raise ValueError("提供的私钥不是RSA类型")

            # Base64解码
            encrypted_bytes = base64.b64decode(encrypted_data.encode("utf-8"))

            # 解密数据
            decrypted_data = private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            return decrypted_data.decode("utf-8")

        except Exception as e:
            logger.warning(f"RSA私钥解密失败: {e}")
            raise

    @staticmethod
    def get_public_key_fingerprint(public_key_pem: str) -> str:
        """获取公钥指纹用于验证

        :param public_key_pem: PEM格式的公钥
        :return: 公钥指纹（SHA256哈希的前16位）
        """
        try:
            # 加载公钥
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode("utf-8"), backend=default_backend()
            )

            # 确保是RSA公钥
            if not isinstance(public_key, RSAPublicKey):
                raise ValueError("提供的公钥不是RSA类型")

            # 获取公钥的DER编码
            public_key_der = public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            # 计算SHA256哈希
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
            digest.update(public_key_der)
            fingerprint = digest.finalize()

            # 返回前16位的十六进制表示
            return fingerprint[:16].hex()

        except Exception as e:
            logger.error(f"获取公钥指纹失败: {e}")
            raise


class RSAPasswordEncryption:
    """RSA密码加密管理器"""

    def __init__(self, private_key_pem: str):
        """初始化RSA密码加密管理器

        :param private_key_pem: 服务端私钥PEM
        """
        self.private_key_pem = private_key_pem
        self.rsa_utils = RSAUtils()

    def decrypt_password(self, encrypted_password: str) -> str:
        """解密前端传来的加密密码

        :param encrypted_password: 前端RSA加密后的密码
        :return: 解密后的明文密码
        """
        return self.rsa_utils.decrypt_with_private_key(encrypted_password, self.private_key_pem)

    def get_public_key_for_frontend(self) -> dict[str, str]:
        """获取前端所需的公钥信息

        :return: 包含公钥和指纹的字典
        """
        # 从私钥提取公钥
        private_key = serialization.load_pem_private_key(
            self.private_key_pem.encode("utf-8"),
            password=None,
            backend=default_backend(),
        )

        # 确保是RSA私钥
        if not isinstance(private_key, RSAPrivateKey):
            raise ValueError("提供的私钥不是RSA类型")

        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        fingerprint = self.rsa_utils.get_public_key_fingerprint(public_pem)

        return {
            "public_key": public_pem,
            "fingerprint": fingerprint,
            "algorithm": "RSA-OAEP-SHA256",
        }


def rsa_password_validator(value: str) -> str:
    """RSA密码验证器"""
    if not isinstance(value, str):
        raise ValueError("密码必须是字符串类型")

    # 如果RSA未启用，直接返回
    if not app_settings.rsa.enabled:
        return value

    try:
        # 尝试RSA解密
        rsa_manager = RSAPasswordEncryption(app_settings.rsa.private_key)
        return rsa_manager.decrypt_password(value)
    except Exception as e:
        logger.debug(f"密码解密失败: {e}")
        raise InvalidInputError("密码解密失败")
