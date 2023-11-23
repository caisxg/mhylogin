"""
对外提供UA信息
参考网站: https://bot.sannysoft.com/
以及: https://pixelscan.net/
"""
from urllib.parse import quote

from user_agents import parse

ua0 = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"

hd0 = {
    "User-Agent": ua0,
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    # 'Accept-Encoding': 'gzip, deflate, br',
    "Referer": "https://user.mihoyo.com/",
    "Origin": "https://user.mihoyo.com",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}


ext_fields0 = {
    "userAgent": ua0,
    "browserScreenSize": 1169820,
    "maxTouchPoints": 0,
    "isTouchSupported": False,
    "browserLanguage": "zh-CN",
    "browserPlat": "MacIntel",  # platform
    "browserTimeZone": "Asia/Shanghai",
    "webGlRender": "ANGLE (Apple, Apple M1, OpenGL 4.1)",
    "webGlVendor": "Google Inc. (Apple)",
    "numOfPlugins": 5,
    "listOfPlugins": [
        "PDF Viewer",
        "Chrome PDF Viewer",
        "Chromium PDF Viewer",
        "Microsoft Edge PDF Viewer",
        "WebKit built-in PDF",
    ],
    "screenRatio": 2,
    "deviceMemory": "8",
    "hardwareConcurrency": "8",
    "cpuClass": "unknown",
    "ifNotTrack": "unspecified",
    "ifAdBlock": 0,
    "hasLiedResolution": 1,
    "hasLiedOs": 0,
    "hasLiedBrowser": 0,
}


def device_info_from_ua(ua=hd0["User-Agent"]):
    ug = parse(hd0["User-Agent"])
    device_model = quote(f"{ug.browser.family} {ug.browser.version_string}")
    device_name = quote(ug.browser.family)
    try:
        os_name = ug.os.family.split(" ", 1)[1]
    except:
        os_name = ug.os.family.split(" ", 1)[0]
    device_os = quote(f"{os_name} {ug.os.version_string} 64-bit")

    device_info = {
        "device_model": device_model,
        "device_name": device_name,
        "device_os": device_os,
    }
    return device_info


device_info0 = device_info_from_ua(hd0["User-Agent"])
__all__ = ["hd0", "ext_fields0", "device_info0"]
