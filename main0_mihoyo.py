import json
import os
import random
import re
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


def from_mihoyo_get_cook(uid, verbose_log=True, **kwargs):
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
    ######################################################################
    ##### 加密, 这里不要用 js , 因为 js会识别设备等信息, 导致加密的结果不一样, 直接使用公钥加密即可
    enpassword = crack_pwd(str(password))
    ######################################################################
    ### 正式开始构造请求 ####
    ######### 1. 先获取一下信息(打个招呼) #################
    get_sleep_time(0, 1)

    cookies = {"_MHYUUID": UUID, "DEVICEFP": DEVICEFP}
    headers = {
        "User-Agent": hd0["User-Agent"],
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        # 'Accept-Encoding': 'gzip, deflate, br',
        "Referer": "https://user.mihoyo.com/",
        "Origin": "https://user.mihoyo.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "sec-ch-ua": hd0["sec-ch-ua"],
        "sec-ch-ua-mobile": hd0["sec-ch-ua-mobile"],
        "sec-ch-ua-platform": hd0["sec-ch-ua-platform"],
    }

    # session.headers.update(headers)
    custom.update_session_headers(session, headers)
    custom.update_session_cookies(session, cookies)

    log.info(f"更新后的 head: {session.headers}")
    log.info(f"更新后的 cook: {session.cookies}")

    params = {"platform": "4"}
    url01 = "https://public-data-api.mihoyo.com/device-fp/api/getExtList"
    response01 = session.get(url=url01, params=params)

    if verbose_log:
        log.info(f"response01.status_code: {response01.status_code}")
        log.info(f"response01.text: {response01.text}")

    #####

    ##### 2.获取法律协议 #################
    get_sleep_time(0, 1)
    url02 = "https://webstatic.mihoyo.com/admin/mi18n/plat_cn/m202004281054311/m202004281054311-zh-cn.json"
    response02 = session.get(url=url02, params="")
    if verbose_log and False:
        log.info(f"response2.json(): {json.dumps(response02.json(), ensure_ascii=False ) }")

    ############### 3.发送 options 请求, 获取 aliyungf_tc 参数 #################
    get_sleep_time(0, 1)
    newhd = {
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    custom.update_session_headers(session, newhd)

    url03 = "https://public-data-api.mihoyo.com/device-fp/api/getFp"
    response03 = session.options(url03, cookies={})

    try:
        # requests 采用的是 cookiesjar 来处理 cookies
        ckdict = custom.cookie2dict(session)
        aliyungf_tc03 = ckdict["aliyungf_tc"]
        if verbose_log:
            log.info(f"aliyungf_tc03: {aliyungf_tc03}")
    except:
        # httpx 采用的是 cookies 类来处理 cookies
        # 从中,可以看出二者获取 cookies 的方式不一样
        log.info(f"获取 aliyungf_tc 失败: {session.cookies.get('aliyungf_tc')}")
        log.error("获取 aliyungf_tc 失败")

    ######### 4. 发送 post 请求, 获取 device_fp 参数 #################
    get_sleep_time(0, 1)

    ck = {
        "_MHYUUID": UUID,
        "DEVICEFP": DEVICEFP,
        "aliyungf_tc": aliyungf_tc03,
        "DEVICEFP_SEED_ID": DEVICEFP_SEED_ID,
        "DEVICEFP_SEED_TIME": DEVICEFP_SEED_TIME,
    }

    custom.update_session_cookies(session, ck)

    ext_fields = ext_fields0
    json_data = {
        "device_id": UUID,
        "seed_id": DEVICEFP_SEED_ID,
        "seed_time": DEVICEFP_SEED_TIME,
        "platform": "4",
        "device_fp": DEVICEFP,
        "app_name": "account",
        "ext_fields": json.dumps(ext_fields, separators=(",", ":")),
    }

    url04 = url03
    response04 = session.post(url04, json=json_data)

    try:
        device_fp = jsonpath(response04.json(), "$..device_fp")[0]
    except:
        log.error("获取 device_fp 失败")
        assert False, "获取 device_fp 失败"

    custom.update_session_cookies(session, {"DEVICEFP": device_fp})

    ######### 5.发送 options 请求
    get_sleep_time(0, 1)

    newhd = {
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "x-rpc-client_type,x-rpc-device_fp,x-rpc-device_id,x-rpc-device_model,x-rpc-device_name,x-rpc-source",
    }
    custom.update_session_headers(session, newhd)

    now = str(int(time.time() * 1000))
    params = {
        "scene_type": "1",
        "now": now,
        "reason": "user.miyoushe.com#/login/password",
        "action_type": "login_by_password",
        "account": username,
        "t": now,
    }
    url05 = "https://webapi.account.mihayo.com/Api/create_mmt"
    # url05 = f"https://webapi.account.mihoyo.com/Api/create_mmt?scene_type=1&now={now}&reason=user.mihoyo.com%23%2Flogin%2Fpassword&action_type=login_by_password&account={username}&t={now}"
    response05 = session.options(url05, params=params, cookies={})
    if verbose_log:
        log.info(f"response05.status_code: {response05.status_code}")

    ###### 6. 发送 get 请求, 获取 mmt_key 参数 #################
    get_sleep_time(0, 1)

    custom.update_session_cookies(session, {"DEVICEFP_SEED_TIME": str(int(time.time() * 1000))})
    if verbose_log:
        ckk = custom.cookie2dict(session)

    ug = parse(hd0["User-Agent"])
    device_model = quote(f"{ug.browser.family} {ug.browser.version_string}")
    device_name = quote(ug.browser.family)

    hd = {
        "Accept-Encoding": "gzip, deflate, br",
        "x-rpc-device_id": ckk["_MHYUUID"],
        "x-rpc-device_model": device_model,  # 设备的型号
        "x-rpc-device_name": device_name,  # 设备的名称
        "x-rpc-client_type": "4",
        "x-rpc-device_fp": ckk["DEVICEFP"],
        "x-rpc-source": "accountWebsite",
    }

    custom.update_session_headers(session, hd)

    #####################################
    now = str(int(time.time() * 1000))
    url06 = url05
    response06 = session.get(url06, params=params, cookies={})
    try:
        mmt_key = jsonpath(response06.json(), "$..mmt_key")[0]
        if verbose_log:
            log.info(f"mmt_key: {mmt_key}")
    except:
        log.error("获取 mmt_key 失败")

    try:
        ckdit = custom.cookie2dict(session)
        aliyungf_tc06 = ckdit["aliyungf_tc"]
        gt = jsonpath(response06.json(), "$..gt")  # 检查是否需要验证码

        if gt:
            log.info("遇见有 gt, 需要验证码")  # 一般情况下不会出现这种情况,
            ### 如果验证码是:  0b2abaab0ad3f4744ab45342a2f3d409  说明 ip 被识别了
            log.info(f"gt: {gt}")
            if "0b2abaab0ad3f4744ab45342a2f3d409" in gt:
                assert False, "ip 被识别了, 请更换 ip"
            # 如果出现 一般是 ip 被识别了, 比如腾讯云的 ip
            # 调用打码平台
        else:
            if verbose_log:
                log.info("没有遇见 gt, 则不需要验证码")
    except:
        log.error("获取 aliyungf_tc或者 gt 失败")
        assert False, "获取 aliyungf_tc或者 gt 失败"

    ######### 7. 发送 options 请求

    newhd = {
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "x-rpc-client_type,x-rpc-device_fp,x-rpc-device_id,x-rpc-device_model,x-rpc-device_name,x-rpc-game_biz,x-rpc-source",
    }
    custom.update_session_headers(session, newhd)

    get_sleep_time(0, 1)
    url07 = "https://webapi.account.mihoyo.com/Api/login_by_password"
    response07 = session.options(url07, cookies={})
    if verbose_log:
        log.info(f"response07.status_code: {response07.status_code}")

    ######### 8.发送 post 请求, 获取最终的登录结果 #################
    time.sleep(random.randint(2, 5))

    seed_time = str(int(time.time() * 1000))
    custom.update_session_cookies(session, {"DEVICEFP_SEED_TIME": seed_time, "aliyungf_tc": aliyungf_tc06})

    custom.update_session_headers(
        session,
        {
            "x-rpc-game_biz": "account_cn",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
    )

    data = {
        "account": username,
        "password": enpassword,
        "is_crypto": "true",
        "mmt_key": mmt_key,
        "source": "user.mihoyo.com",
        "t": str(int(time.time() * 1000)),
    }
    time.sleep(random.uniform(1, 3))
    url08 = url07
    response08 = session.post(url08, data=data)

    if "手机短信登录" in response08.json()["data"]["msg"]:
        log.error("登录失败, 请使用手机短信登录")
        assert False, "登录失败, 请使用手机短信登录"

    ## 登录成功后, 保存 cookies
    try:
        log.info(f"response08.json(): {json.dumps(response08.json(), ensure_ascii=False ) }")
        log.info("登录成功")
    except:
        log.error("登录失败")
        assert False, "登录失败"

    try:
        arrayhandler = ArrayObjectHandler(filename=op_cookie_file)
        ck00 = custom.cookie2dict(session)
        arrayhandler.update_data(uid, "mihoyo", ck00)
        arrayhandler.save_to_json(op_cookie_file)
        log.info("保存 cookies, 成功")
    except:
        log.error("保存 cookies 失败")

    time.sleep(random.randint(14, 28))

    session.close()
    return ck00


if __name__ == "__main__":
    verbose_log = True
    uid = 1
    ck00 = from_mihoyo_get_cook(uid=uid, verbose_log=verbose_log, forcerefresh=True, enable=True)
    log.info(f"ck00: {ck00}")
