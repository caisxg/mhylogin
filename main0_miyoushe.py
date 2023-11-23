import json
import os
import random
import sys
import time
from pathlib import Path
from urllib.parse import quote

import execjs
import requests
from jsonpath import jsonpath
from user_agents import parse

from enrsapw import crack_pwd
from init import ArrayObjectHandler, ProjectInfoGetter, ProxyInfo
from myrequest import CustomSession, SessionInitializer
from utils.loghelper import log
from utils.tool import append_to_json, get_sleep_time, read_yaml_file
from utils.UAinfo import ext_fields0, hd0


def from_miyoushe_get_cook(uid, verbose_log=True, **kwargs):
    sessioninit = SessionInitializer(uid=uid, **kwargs)
    session, custom, prodata, uid, username, password = sessioninit.initialize_session()

    op_cookie_file = prodata.op_cookie_file
    pj_dir = prodata.pj_dir
    log.info(f"\n当前项目信息: {prodata}")
    log.info(f"当前文件所获取的pro_dir: {pj_dir}")

    # 0.2. 调用 js 伪造参数  --- 准备参数
    # 读取本地的JavaScript文件
    jsfile = os.path.join(pj_dir, "js", "fake_infobyjs.js")
    with open(jsfile, "r", encoding="utf-8") as js_file:
        js_code = js_file.read()

    # 执行JavaScript代码
    ctxt = execjs.compile(js_code)

    # 调用JavaScript函数
    UUID = ctxt.call("getUuid")
    DEVICEFP_SEED_ID = ctxt.call("getRandomNumber", 16)
    DEVICEFP = ctxt.call("getRandomNumber10Radix", 10)
    DEVICEFP_SEED_TIME = str(int(time.time() * 1000))
    ##### 加密, 这里不要用 js , 因为 js会识别设备等信息, 导致加密的结果不一样, 直接使用公钥加密即可
    enaccount = crack_pwd(str(username))
    enpassword = crack_pwd(str(password))
    ################### 1. 获取 aliyungf_tc 参数 ###################

    get_sleep_time()

    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Origin": "https://www.miyoushe.com",
        "Pragma": "no-cache",
        "Referer": "https://www.miyoushe.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": hd0["User-Agent"],
        "sec-ch-ua": hd0["sec-ch-ua"],
        "sec-ch-ua-mobile": hd0["sec-ch-ua-mobile"],
        "sec-ch-ua-platform": hd0["sec-ch-ua-platform"],
    }
    params = {"platform": "4"}

    custom.update_session_headers(session, headers)

    url0 = "https://public-data-api.mihoyo.com/device-fp/api/getExtList"
    response01 = session.get(url0, params=params)

    # 这里会获得 aliyungf_tc 参数
    try:
        ckdict = custom.cookie2dict(session)
        aliyungf_tc01 = ckdict["aliyungf_tc"]
        if verbose_log:
            log.info(f"aliyungf_tc01: {aliyungf_tc01}")
    except:
        log.error("aliyungf_tc01 获取失败")

    ####################### 2 获取发送 option--准备获取 device_fp #######################
    get_sleep_time()
    newhd = {
        "Access-Control-Request-Headers": "content-type",
        "Access-Control-Request-Method": "POST",
    }
    custom.update_session_headers(session, newhd)
    url02 = "https://public-data-api.mihoyo.com/device-fp/api/getFp"
    response02 = session.options(url02)
    if verbose_log:
        log.info(f"response02.status_code: {response02.status_code}")

    ####################### 3 获取 device_fp 参数 #######################
    custom.update_session_headers(session, {"Content-Type": "application/json;charset=UTF-8"})

    ext_fields = ext_fields0
    json_data = {
        "device_id": UUID,
        "seed_id": DEVICEFP_SEED_ID,
        "seed_time": DEVICEFP_SEED_TIME,
        "platform": "4",
        "device_fp": DEVICEFP,
        "app_name": "bbs_cn",
        "ext_fields": json.dumps(ext_fields, separators=(",", ":")),
    }

    get_sleep_time()
    url03 = url02
    response03 = session.post(url03, json=json_data)
    # 这里会获得device_fp参数
    res03_json = response03.json()
    try:
        device_fp = jsonpath(res03_json, "$..device_fp")[0]
        if verbose_log:
            log.info(f"device_fp: {device_fp}")
    except:
        log.info(f"device_fp 获取失败")

    #########################################################
    # 4. 发送 options 请求  --  获取登录所需的参数

    newhd = {
        "Access-Control-Request-Headers": "content-type,x-rpc-app_id,x-rpc-client_type,x-rpc-device_fp,x-rpc-device_id,x-rpc-device_model,x-rpc-device_name,x-rpc-device_os,x-rpc-game_biz,x-rpc-mi_referrer,x-rpc-sdk_version,x-rpc-source",
        "Access-Control-Request-Method": "POST",
    }

    custom.update_session_headers(session, newhd)

    get_sleep_time()
    url04 = "https://passport-api.miyoushe.com/account/ma-cn-passport/web/loginByPassword"
    response04 = session.options(url04)
    if verbose_log:
        log.info(f"response04: {response04}")

    #########################################################
    # 5. 构造登录请求 --
    #########################################################
    newtime = str(int(time.time() * 1000))
    nn2 = str(int(time.time()))

    status = {
        "bll8iq97cem8": {
            "sms_login_tab": True,
            "pwd_login_tab": True,
            "password_reset_entry": True,
            "qr_login": True,
        }
    }
    ck = {
        "_MHYUUID": UUID,
        "DEVICEFP_SEED_ID": DEVICEFP_SEED_ID,
        "DEVICEFP_SEED_TIME": newtime,
        "DEVICEFP": device_fp,
        "_ga": "GA1.1.1479607327." + nn2,  # 可以不要
        "_ga_KS4J8TXSHQ": f"GS1.1.{nn2}.1.0.{nn2}.0.0.0",  # 可以不要
        "LOGIN_PLATFORM_SWITCH_STATUS": json.dumps(status, separators=(",", ":")),
        # "LOGIN_PLATFORM_SWITCH_STATUS": "{%22bll8iq97cem8%22:{%22sms_login_tab%22:true%2C%22pwd_login_tab%22:true%2C%22password_reset_entry%22:true%2C%22qr_login%22:true}}",
    }

    custom.update_session_cookies(session, ck)
    ug = parse(hd0["User-Agent"])
    device_model = quote(f"{ug.browser.family} {ug.browser.version_string}")
    device_name = quote(ug.browser.family)
    try:
        os_name = ug.os.family.split(" ", 1)[1]
    except:
        os_name = ug.os.family.split(" ", 1)[0]
    device_os = quote(f"{os_name} {ug.os.version_string} 64-bit")

    hd5 = {
        "x-rpc-app_id": "bll8iq97cem8",  # 固定参数(js 产生的), 感觉 pc 和手机端是不一样的
        "x-rpc-client_type": "4",
        "x-rpc-device_fp": device_fp,
        "x-rpc-device_id": UUID,
        "x-rpc-device_model": device_model,
        "x-rpc-device_name": device_name,
        "x-rpc-device_os": device_os,  # "OS%20X%2010.15.7%2064-bit",
        "x-rpc-game_biz": "bbs_cn",  # 固定参数(js 产生的), 感觉 pc 和手机端是不一样的
        # 这个参数本质上就是登录页面的url(只不过我们一般登录的时候是弹窗的形式,所以这个参数是弹窗的url)
        "x-rpc-mi_referrer": "https://user.miyoushe.com/login-platform/index.html?app_id=bll8iq97cem8&app_version=2.57.0&theme=&token_type=4&game_biz=bbs_cn&message_origin=https%253A%252F%252Fwww.miyoushe.com&succ_back_type=message%253Alogin-platform%253Alogin-success&fail_back_type=message%253Alogin-platform%253Alogin-fail&sync_login_status=popup&ux_mode=popup&iframe_level=1&ap_mps=1#/login/password",
        "x-rpc-sdk_version": "2.17.0",
        "x-rpc-source": "v2.webLogin",
    }

    custom.update_session_headers(session, hd5)

    json_data = {"account": enaccount, "password": enpassword}

    get_sleep_time(4, 8)
    url05 = url04
    response05 = session.post(url05, json=json_data)
    try:
        response05str = str(response05.json())
        ck0 = custom.cookie2dict(session)
        if verbose_log:
            log.info(f"response05.json(): {response05str}")
            log.info(f"response05.status_code: {response05.status_code}")
            log.info(f"ck0: {ck0}")
    except:
        log.error("==登录失败==")
        assert False, "==登录失败=="

    if "请求频繁" in response05str:
        log.error("请求频繁")
        assert False, "请求频繁"
    elif "您的账号存在安全风险" in response05str:
        log.error("您的账号存在安全风险")
        assert False, "您的账号存在安全风险"
    elif "密码错误" in response05str:
        log.error("密码错误")
        assert False, "密码错误"
    elif "OK" in response05str and "user_info" in response05str:
        log.info("登录成功, 保存 cookies")
    elif "null" in response05str:
        log.error("登录失败, 值为 null")
        assert False, "登录失败,值为 null"
    else:
        log.error("登录失败")
        assert False, "登录失败"

    ########################################################
    #### 以下可以删除, 仅用于测试
    ############ 06  登录成功后继续获取一些参数 #################
    # 先发送一个 options 请求
    newhd = {
        "Access-Control-Request-Headers": "content-type,ds,x-rpc-app_version,x-rpc-client_type,x-rpc-device_id",
        "Access-Control-Request-Method": "POST",
    }

    custom.update_session_headers(session, newhd)

    url06 = "https://bbs-api.miyoushe.com/user/wapi/login"
    response06 = session.options(url06)

    log.info(f"response06: {response06}")

    ################# 07 获取一些参数 ############################
    newhd = {
        "Content-Type": "application/json;charset=UTF-8",
        "DS": f"{int(time.time())},jwc7iE,0124ddce4db846949e0d34ca0018993b",
        "x-rpc-device_id": UUID.replace("-", ""),
    }

    custom.update_session_headers(session, newhd)
    json_data = {"gids": "2"}

    url07 = url06
    response07 = session.post(url07, json=json_data)
    log.info(f"response07.json(): {json.dumps(response07.json(), ensure_ascii=False)}")

    ################# 08 获取用户信息 ############################
    get_sleep_time()

    custom.update_session_headers(session, {"Accept": "application/json, text/plain, */*"})
    params = {"gids": "2"}
    response08 = session.get("https://bbs-api.miyoushe.com/user/wapi/getUserFullInfo", params=params)

    try:
        if response08.status_code == 200:
            log.info(f"response08.json(): {json.dumps(response08.json(), ensure_ascii=False)}")
            log.info("登录成功")
    except:
        log.error("登录失败")
        assert False, "登录失败"

    # 返回最后的 cookies -- 理论上和ck0没区别
    try:
        arrayhandler = ArrayObjectHandler(filename=op_cookie_file)
        ck00 = custom.cookie2dict(session)
        arrayhandler.update_data(uid, "miyoushe", ck00)
        arrayhandler.save_to_json(op_cookie_file)
        log.info("保存 cookies,  成功")
    except:
        log.error("保存 cookies,  失败")

    time.sleep(random.uniform(12, 18))
    session.close()

    return ck00


if __name__ == "__main__":
    verbose_log = True
    uid = 1
    ck00 = from_miyoushe_get_cook(uid=uid, verbose_log=verbose_log)
    log.info(f"ck00: {ck00}")
