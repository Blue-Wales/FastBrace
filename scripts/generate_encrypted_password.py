#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : FastBrace
@File    : generate_encrypted_password.py
@Author  : bright
@Date    : 2026-08-25
@Desc    : RSA 密码加密工具，用于生成接口测试所需的加密密码

用法:
    python scripts/generate_encrypted_password.py                        # 交互式
    python scripts/generate_encrypted_password.py -p "mypassword"        # 加密单个密码
    python scripts/generate_encrypted_password.py -p p1 p2 p3            # 批量加密
    python scripts/generate_encrypted_password.py -f in.txt -o out.txt   # 从文件读取
"""

import argparse
import getpass
import sys
from pathlib import Path

# 保证从任意目录运行脚本时都能导入项目内的 infrastructure 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger

from infrastructure.core.settings import app_settings
from infrastructure.utils.rsa_utils import RSAPasswordEncryption, RSAUtils

LOGIN_URL = "http://localhost:8000/login"


def encrypt_password(password: str, show_details: bool = False) -> str | None:
    """RSA 加密密码；RSA 未启用时返回明文，加密失败返回 None。"""
    if not app_settings.rsa.enabled:
        logger.warning("RSA 加密未启用，将返回明文密码")
        return password

    try:
        manager = RSAPasswordEncryption(app_settings.rsa.private_key)
        public_key_info = manager.get_public_key_for_frontend()
        encrypted = RSAUtils.encrypt_with_public_key(password, public_key_info["public_key"])

        if show_details:
            logger.info(f"公钥指纹: {public_key_info['fingerprint']}")
            logger.info(f"加密算法: {public_key_info['algorithm']}")
            logger.info(f"加密后密码: {encrypted}")
        return encrypted
    except Exception:
        logger.exception("密码加密失败")
        return None


def _print_curl_example(encrypted: str) -> None:
    """打印 curl 调用示例。"""
    print("\ncurl 测试示例:")
    print(f"curl -X POST {LOGIN_URL} \\")
    print('  -F "username=your_username" \\')
    print(f'  -F "password={encrypted}"')


def interactive_mode() -> None:
    """交互式加密模式。"""
    if not app_settings.rsa.enabled:
        logger.warning("RSA 加密未启用，请检查配置文件中的 rsa.enabled 设置")
        return

    logger.info(f"RSA 加密已启用 (密钥长度: {app_settings.rsa.key_size} 位)")
    while True:
        password = getpass.getpass("请输入要加密的密码 (输入 'quit' 退出): ")
        if password.lower() == "quit":
            logger.info("再见!")
            return
        if not password:
            logger.warning("密码不能为空")
            continue

        encrypted = encrypt_password(password, show_details=True)
        if encrypted:
            print("\n用于 API 测试的加密密码:")
            print(encrypted)
            _print_curl_example(encrypted)


def batch_mode(passwords: list[str]) -> None:
    """批量加密模式。"""
    results: list[tuple[str, str]] = []
    for password in passwords:
        encrypted = encrypt_password(password)
        if encrypted:
            results.append((password, encrypted))

    print("\n批量加密结果:")
    for index, (password, encrypted) in enumerate(results, 1):
        print(f"[{index}] 明文: {password}")
        print(f"    加密: {encrypted}")


def file_mode(input_file: str, output_file: str | None = None) -> None:
    """从文件读取密码列表并加密。"""
    try:
        lines = Path(input_file).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        logger.error(f"文件读取失败: {exc}")
        return

    passwords = [line.strip() for line in lines if line.strip()]
    logger.info(f"读取到 {len(passwords)} 个密码")

    results = []
    for password in passwords:
        encrypted = encrypt_password(password)
        if encrypted:
            results.append(f"{password} -> {encrypted}")

    if output_file:
        try:
            Path(output_file).write_text("\n".join(results) + "\n", encoding="utf-8")
            logger.info(f"结果已保存到: {output_file}")
        except OSError as exc:
            logger.error(f"文件写入失败: {exc}")
    else:
        print("\n加密结果:")
        for result in results:
            print(result)


def main() -> int:
    """脚本入口。"""
    parser = argparse.ArgumentParser(
        description="RSA 密码加密工具 - 用于生成 API 测试所需的加密密码",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "使用示例:\n"
            "  python scripts/generate_encrypted_password.py\n"
            '  python scripts/generate_encrypted_password.py -p "mypassword123"\n'
            '  python scripts/generate_encrypted_password.py -p "pass1" "pass2" "pass3"\n'
            "  python scripts/generate_encrypted_password.py -f passwords.txt -o encrypted.txt"
        ),
    )
    parser.add_argument("-p", "--password", nargs="+", help="要加密的密码（支持多个）")
    parser.add_argument("-f", "--file", help="从文件读取密码列表（每行一个密码）")
    parser.add_argument("-o", "--output", help="输出文件路径（用于文件模式）")
    parser.add_argument("-d", "--details", action="store_true", help="显示详细信息")
    args = parser.parse_args()

    if args.file:
        file_mode(args.file, args.output)
    elif args.password:
        if len(args.password) == 1:
            encrypted = encrypt_password(args.password[0], args.details)
            if encrypted:
                print(encrypted)
        else:
            batch_mode(args.password)
    else:
        interactive_mode()
    return 0


if __name__ == "__main__":
    sys.exit(main())
