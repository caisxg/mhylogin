"""
这个文件,是用于上层调用的, 用于识别米游社签到而准备的
"""
import json
import os
import random
import sys
import time

import requests
from loguru import logger
from twocaptcha import TwoCaptcha

try:
    from captchakey import apikey
except:
    try:
        
        from mhylogin.captchakey import apikey
        logger.warning("找到环境变量中的APIKEY_2CAPTCHA")
    except:
        apikey = None
        logger.warning("未找到验证码APIKEY, 请在环境变量中设置APIKEY_2CAPTCHA")


api_key = os.getenv('APIKEY_2CAPTCHA', apikey)
solver = TwoCaptcha(api_key)

def game_captcha2(gt: str, challenge: str):
    logger.warning("开始验证验证码1")
    logger.info(f"gt: {gt}")
    logger.info(f"challenge: {challenge}")
    time.sleep(random.randint(3, 6))
    result = solver.geetest(gt=gt,
                apiServer='api.geetest.com',
                challenge=challenge,
                url='https://2captcha.com/demo/geetest'
                )
    logger.warning(f"验证码 1 返回的结果 result: {result}")
    rep = json.loads(result["code"])
    logger.warning(f"验证码 1 返回的结果rep: {rep}")
    return rep["geetest_validate"]
    # return None  # 失败返回None 成功返回validate


def bbs_captcha2(gt: str, challenge: str):
    logger.warning("开始验证验证码2")
    logger.info(f"gt: {gt}")
    logger.info(f"challenge: {challenge}")
    time.sleep(random.randint(3, 6))
    result = solver.geetest(gt=gt,
                    apiServer='api.geetest.com',
                    challenge=challenge,
                    url='https://2captcha.com/demo/geetest'
                    )
    logger.warning(f"验证码 2 返回的结果 result: {result}")
    rep = json.loads(result["code"])
    logger.warning(f"验证码 2 返回的结果rep: {rep}")
    return rep["geetest_validate"]
