"""
加密工具模块
用于处理敏感数据的加密和解密
"""

import base64
import os
from cryptography.fernet import Fernet


def get_encryption_key() -> bytes:
    """获取加密密钥，如果不存在则生成一个新的"""
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        # 在生产环境中，这个密钥应该从安全的地方获取
        # 这里只是示例，实际应用中需要更安全的密钥管理
        key = Fernet.generate_key().decode()
        # 你可能想要将这个密钥保存到环境变量或安全存储中
    return key.encode() if isinstance(key, str) else key


def encrypt_text(text: str) -> str:
    """加密文本"""
    if not text:
        return ""

    key = get_encryption_key()
    f = Fernet(key)
    encrypted_text = f.encrypt(text.encode())
    return base64.urlsafe_b64encode(encrypted_text).decode()


def decrypt_text(encrypted_text: str) -> str:
    """解密文本"""
    if not encrypted_text:
        return ""

    try:
        key = get_encryption_key()
        f = Fernet(key)
        decoded_text = base64.urlsafe_b64decode(encrypted_text.encode())
        decrypted_text = f.decrypt(decoded_text)
        return decrypted_text.decode()
    except Exception:
        # 如果解密失败，返回空字符串
        return ""
