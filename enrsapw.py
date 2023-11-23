##########################
### 加密方式 3: 采用 Crypto 包(第三方的) --- 可以用, 使用 与PKCS1_v1_5填充
import base64
import os
import sys
from pathlib import Path

from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA


def crack_pwd(pwd: str):
    key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDDvekdPMHN3AYhm/vktJT+YJr7
cI5DcsNKqdsx5DZX0gDuWFuIjzdwButrIYPNmRJ1G8ybDIF7oDW2eEpm5sMbL9zs
9ExXCdvqrn51qELbqj0XxtMTIpaCHFSI50PfPpTFV9Xt/hmyVwokoOXFlAEgCn+Q
CgGs52bFoYMtyi+xEQIDAQAB
-----END PUBLIC KEY-----
"""
    # 注意上述key的格式
    rsakey = RSA.importKey(key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
    cipher_text = base64.b64encode(cipher.encrypt(pwd.encode("utf-8")))  # 对传递进来的用户名或密码字符串加密
    value = cipher_text.decode("utf8")  # 将加密获取到的bytes类型密文解码成str类型
    return value


__all__ = ["crack_pwd"]
