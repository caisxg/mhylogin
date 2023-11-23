"""
这个文件,是用于本层调用的, 用于识别米游社登录以及通行证登录准备的
"""
import ast
import base64
import json
import random
import sys
import time
import uuid

import requests
from jsonpath import jsonpath
from twocaptcha import TwoCaptcha

from captchakey import apikey
from utils.loghelper import log


def btoa(input_string):
    # 将字符串转换为字节流
    input_bytes = input_string.encode("utf-8")
    # 使用base64进行编码
    encoded_bytes = base64.b64encode(input_bytes)
    # 将字节流转换回字符串并返回
    return encoded_bytes.decode("utf-8")

# 下面这个 api 接口稳定很多
def yun_captcha(gt, use_v4=True, gtdict=None, challenge=None):
    api_key = apikey
    solver = TwoCaptcha(api_key)
    new_uuid = uuid.uuid4()
    result = solver.geetest_v4(captcha_id=gt, url="https://2captcha.com/demo/geetest-v4", challenge=str(new_uuid))
    cleaned = ast.literal_eval(result["code"])
    log.warning(f"验证码返回的结果 cleaned: {cleaned}")  # 同上
    assert isinstance(cleaned, dict), "验证码返回的结果不是字典"
    return cleaned
