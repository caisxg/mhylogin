import datetime
import json
import logging
import os
import random
import time

import pytz
import requests
import yaml

from utils.loghelper import log


class ArrayObjectHandler:
    def __init__(self, data=None, filename=None):
        # data 和 filename 二选一
        if data is not None and filename is not None:
            raise ValueError("Only one of 'data' and 'filename' should be provided.")

        self.filename = filename
        self.data = data or []

        if filename is not None:
            if os.path.exists(filename):
                self.read_from_json(filename)
            else:
                self.data = []

    def update_data(self, uid, field, update_data):
        found = False
        for entry in self.data:
            if str(entry["uid"]) == str(uid):
                entry[field] = update_data
                found = True
                break

        if not found:
            new_entry = {"uid": uid, "mihoyo": {}, "miyoushe": {}, "yunys": {}}
            new_entry[field] = update_data
            self.data.append(new_entry)

    def select_by_uid(self, uid):
        for entry in self.data:
            if str(entry["uid"]) == str(uid):
                return entry
        assert False, f"Entry with uid '{uid}' not found."
        # return None  # 如果找不到对应 uid 的 entry，返回 None 或者其他合适的默认值

    def delete_by_uid(self, uid):
        self.data = [entry for entry in self.data if entry["uid"] != uid]

    def save_to_json(self, filename):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=2)

    def read_from_json(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except:
            log.error(f"Error reading {filename}")

    def __str__(self) -> str:
        return str(self.data)


## 用于获取项目的根目录,把项目的信息存储到类中
class ProjectInfoGetter:
    def __init__(self, username=None):
        self.username = username
        self.pj_dir = self.get_project_directory()
        self.op_proxy_file = os.path.join(self.pj_dir, "outputjson", "proxy_info.json")
        self.op_cookie_file = os.path.join(self.pj_dir, "outputjson", "user_cookies.json")
        self.in_proxy_file = os.path.join(self.pj_dir, "inputyaml", "proxyinfo.yaml")
        self.in_userinfo_file = os.path.join(self.pj_dir, "inputyaml", "userinfo.yaml")
        #创建文件夹
        os.makedirs(os.path.dirname(self.op_proxy_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.op_cookie_file), exist_ok=True)
        self._check_files_exist = self.check_files_exist()
        self.data = {
            "pj_dir": self.pj_dir,
            "op_proxy_file": self.op_proxy_file,
            "op_cookie_file": self.op_cookie_file,
            "in_proxy_file": self.in_proxy_file,
            "in_userinfo_file": self.in_userinfo_file,
        }

    def get_project_directory(self):
        # 用于获取项目的根目录
        try:
            current_directory = os.path.dirname(os.path.realpath(__file__))
            # parent_directory = os.path.dirname(current_directory)
            return os.path.abspath(current_directory)
        except:
            current_directory = os.getcwd()
            return os.path.abspath(current_directory)

    def check_files_exist(self):
        # 用于检查文件是否存在
        assert os.path.exists(self.pj_dir), f"Project directory '{self.pj_dir}' does not exist."
        assert os.path.exists(self.in_proxy_file), f"Proxy info file '{self.in_proxy_file}' does not exist."
        assert os.path.exists(self.in_userinfo_file), f"User info file '{self.in_userinfo_file}' does not exist."
        return True

    def get_project_info(self):
        # 用于获取所有项目信息
        return {
            "pj_dir": self.pj_dir,
            "op_proxy_file": self.op_proxy_file,
            "op_cookie_file": self.op_cookie_file,
            "in_proxy_file": self.in_proxy_file,
            "in_userinfo_file": self.in_userinfo_file,
        }

    def __str__(self):
        # 用于将对象转为字符串表示形式
        project_info = self.get_project_info()
        return json.dumps(project_info, indent=2)


### 代理文件的读取, 然后把文件内容转为类的属性
class ProxyInfo:
    def __init__(self, in_proxy_file=None, enable=True):
        self.enable = enable
        self.username = None
        self.password = None
        self.api_url = None
        self.valid_minutes = None
        if self.enable:
            self.read_proxy_info_from_yaml(in_proxy_file)
        else:
            self.username = None
            self.password = None
            self.api_url = None
            self.valid_minutes = None

    def read_proxy_info_from_yaml(self, in_proxy_file):
        if in_proxy_file is None or not os.path.exists(in_proxy_file):
            log.warning(f"代理文件不存在: {in_proxy_file}, 无法启用代理")
            self.enable = False
            return None

        with open(in_proxy_file, "r", encoding="utf-8") as f:
            in_proxy_info = yaml.load(f.read(), Loader=yaml.FullLoader)

        if not in_proxy_info["proxy"]["enable"]:
            log.warning("代理未启用")
            self.enable = False
        else:
            self.enable = True
            self.username = in_proxy_info["proxy"]["username"]
            self.password = in_proxy_info["proxy"]["password"]
            self.api_url = in_proxy_info["proxy"]["api_url"]
            self.valid_minutes = in_proxy_info["proxy"]["valid_minutes"]
        return None

    def __str__(self):
        return json.dumps(self.__dict__, indent=2)


class ProxyManager:
    def __init__(self, username=None, forcerefresh=False, enable=True):
        """
        参数说明:
        username: 用于区分不同的用户, 一般是用户的账号
        forcerefresh: 是否强制刷新代理
        enable: 是否启用代理, 默认启用
        """

        self.username = username
        ## 项目 信息设置
        self.projectinfo = ProjectInfoGetter(self.username)
        ## 如果代理信息设置
        self.proxyinfo = ProxyInfo(self.projectinfo.in_proxy_file, enable)

        ## 不同格式的代理信息
        ## PROX 表示最原始的代理信息, 来自于代理提供商, 表示 proxy_info.json 文件中的内容
        self.forcerefresh = forcerefresh
        if enable:
            self.PROX = self.get_valid_proxy_with_parm()

            self.proxy = self.PROX.get("proxy", None)  # 一般用于 requests
            if self.proxy is None:
                log.error("代理为空")
            self.proxy_request = None
            self.proxy_httpx = None
            self.check_proxy()
        else:
            self.PROX = None
            self.proxy = None
            self.proxy_request = None
            self.proxy_httpx = None

    def convert_timestamp_to_beijing_time(self, timestamp):
        # Convert Unix timestamp to datetime
        utc_datetime = datetime.datetime.utcfromtimestamp(timestamp)
        # Set the timezone to Beijing
        beijing_timezone = pytz.timezone("Asia/Shanghai")
        beijing_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(beijing_timezone)
        beijing_time_str = beijing_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")

        return beijing_time_str

    def get_random_proxy_with_auth(self, api_url, username, password):
        timeout_seconds = 30
        proxy_ip = requests.get(api_url, timeout=timeout_seconds).json()["data"]["proxy_list"]
        proxy = random.choice(proxy_ip)
        tmpproxies = {
            "http": f"http://{username}:{password}@{proxy}",
            "https": f"http://{username}:{password}@{proxy}",
        }
        now_timestamp = int(time.time())
        PROX = {"timestamp": now_timestamp, "beijingtime": self.convert_timestamp_to_beijing_time(now_timestamp), "proxy": tmpproxies}
        self.save_proxy_info_to_json(PROX, self.projectinfo.op_proxy_file)
        return PROX

    def save_proxy_info_to_json(self, proxyinfo, proxy_file):
        with open(proxy_file, "w", encoding="utf-8") as json_file:
            json.dump(proxyinfo, json_file, indent=4)

    def load_proxy_info_from_json(self, op_proxy_file):
        with open(op_proxy_file, "r", encoding="utf-8") as json_file:
            proxyinfo = json.load(json_file)
        return proxyinfo

    def is_cached_proxy_valid(self, op_proxy_file, valid_minutes):
        try:
            PROX = self.load_proxy_info_from_json(op_proxy_file)
            timestamp = PROX.get("timestamp", 0) + valid_minutes * 60
            current_time = int(time.time())
            if timestamp > current_time:
                log.warning("使用缓存")
                return True
            else:
                log.warning("缓存的代理时间到期")
                return False
        except Exception as e:
            log.warning(f"Invalid proxy info: {e}")
            return False

    def get_valid_proxy_with_parm(self):
        if not self.proxyinfo.enable:
            log.info("代理未启用")
            return None

        op_proxy_file = str(self.projectinfo.op_proxy_file)
        api_url = str(self.proxyinfo.api_url)
        username = str(self.proxyinfo.username)
        password = str(self.proxyinfo.password)
        valid_minutes = int(self.proxyinfo.valid_minutes)
        try:
            if self.forcerefresh or not self.is_cached_proxy_valid(op_proxy_file, valid_minutes):
                log.info("Refreshing proxy...")
                PROX = self.get_random_proxy_with_auth(api_url, username, password)
            else:
                log.info("Using cached proxy...")
                PROX = self.load_proxy_info_from_json(op_proxy_file)
            return PROX
        except Exception as e:
            log.error(f"Error getting valid proxy: {e}")
            return None

    def check_proxy(self):
        try:
            ## 简单的检查一下,代理是否可用
            Headers = {
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
            }
            resp = requests.get("https://www.baidu.com", headers=Headers, proxies=self.proxy, timeout=5)

            assert resp.status_code == 200
            self.proxy_request = self.proxy
            self.proxy_httpx = {"http://": self.proxy["http"], "https://": self.proxy["https"]}
            log.info("代理成功通过检测!!!")
            log.info(f"结果status_code: {resp.status_code}")
        except:
            log.error("~~代理出错!!")
            self.proxy = None
            self.proxy_request = None
            self.proxy_httpx = None


# 使用示例
if __name__ == "__main__":
    # 项目信息
    project_info_getter = ProjectInfoGetter()
    print(project_info_getter)

    # 一个用来存储数组对象的文件

    # 代理
    proxy_manager = ProxyManager()
    print(proxy_manager.proxy)
    print(proxy_manager.proxy_request)
    print(proxy_manager.proxy_httpx)
    print(proxy_manager.PROX)
    print(proxy_manager.projectinfo)
    print(proxy_manager.proxyinfo)
