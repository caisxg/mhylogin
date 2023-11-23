import os

import chardet
import httpx
import requests

from init import ArrayObjectHandler, ProjectInfoGetter, ProxyInfo, ProxyManager
from utils.loghelper import log
from utils.tool import get_sleep_time, read_yaml_file


class CustomSession:
    def __init__(self, username=None, forcerefresh=False, enable=True):
        self.proxy_manager = ProxyManager(username, forcerefresh, enable)
        if enable:
            self.proxy_request = self.proxy_manager.proxy_request
            self.proxy_httpx = self.proxy_manager.proxy_httpx
        else:
            self.proxy_request = None
            self.proxy_httpx = None

    def get_new_session(self, userequests=False, verbose=False):
        if userequests:
            return self._get_requests_session(verbose)
        else:
            return self._get_httpx_session(verbose)

    ######### requests 的实现 #########
    def _get_requests_session(self, verbose):
        session = requests.Session()
        if verbose:
            session.hooks["response"] = [self._request_log_resp]
        session.mount("http://", requests.adapters.HTTPAdapter(max_retries=10))
        session.mount("https://", requests.adapters.HTTPAdapter(max_retries=10))
        if self.proxy_request is not None:
            session.proxies.update(self.proxy_request)

        return session

    def _request_log_resp(self, r, *args, **kwargs):
        # requests 只提供了一个钩子: response
        req = r.request
        log.info(f"  +>>请求url: {req.method} {req.url}")
        log.info(f"  +>>请求头: {req.headers}")
        log.info(f"  +>>请求ck: {req._cookies.get_dict()}")
        log.info("   +>><<+    以下是响应内容    +>><<+ ")
        log.info(f"  <<+响应状态: {r.status_code}")
        log.info(f"  <<+响应请求头: {r.headers}")
        log.info(f"  <<+响应内容: {r.content}")
        log.info(f"  <<+响应cookies: {r.cookies.get_dict()}")

    ######### httpx 的实现 #########
    def _httpx_log_request(self, request):
        # 实现自定义的请求日志逻辑
        log.info(f"  >>>发送url: {request.method} {request.url}")
        log.info(f"  >>>发送请求头: {request.headers}")
        log.info(f"  >>>发送内容: {request.content}")

    def _httpx_log_response(self, response):
        # 要访问事件钩子中的响应体，则需要调用 response.read() 方法
        # 如果是异步,则需要调用  response.aread().
        # 钩子也允许修改 request 和 response 对象。
        request = response.request
        response.read()  # 读取响应内容，否则下次请求会出错
        log.info(f"  <<<Status {response.status_code} {response.reason_phrase}")
        log.info(f"  <<<对应url: {request.method} {request.url}")
        log.info(f"  <<<响应头: {response.headers}")
        log.info(f"  <<<响应内容: {response.text}")
        log.info(f"  <<<响应cookies: {response.cookies}")

    def _autodetect(self, content):
        return chardet.detect(content).get("encoding")

    def _get_httpx_session(self, verbose):
        http_args = {"timeout": 20, "transport": httpx.HTTPTransport(retries=10), "follow_redirects": True, "verify": False, "default_encoding": self._autodetect}

        if verbose:
            event_hooks = {
                "request": [self._httpx_log_request],
                "response": [self._httpx_log_response],
            }
            http_args["event_hooks"] = event_hooks

        http_args["http2"] = True
        if self.proxy_httpx is not None:
            http_args["proxies"] = self.proxy_httpx

        assert isinstance(http_args["proxies"], dict)

        http = httpx.Client(**http_args)
        if self.proxy_httpx is not None:
            http.proxies = self.proxy_httpx
        else:
            http.proxies = None
        # Headers = {
        #     "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
        # }
        # rep = http.get(url="https://www.baidu.com", headers=Headers)
        # log.error(f"使用rep, {rep}")
        return http

    def set_response_encoding(self, response):
        if isinstance(response, httpx.Response):
            return response

        elif isinstance(response, requests.models.Response):
            try:
                # Use chardet to detect the encoding
                encoding_detection = chardet.detect(response.content)
                detected_encoding = encoding_detection["encoding"]
                # Set the detected encoding
                response.encoding = detected_encoding
            except:
                response.encoding = "utf-8"
            return response
        else:
            log.warning("有问题")
            return response

    def get_session_cookies(self, session):
        if isinstance(session, requests.sessions.Session):
            return session.cookies
        elif isinstance(session, httpx.Client):
            return httpx.Cookies(session.cookies)
        else:
            log.error("出错了")

    def update_session_cookies(self, session, addcook=None):
        assert isinstance(addcook, dict)

        if isinstance(session, requests.sessions.Session):
            session.cookies.update(addcook)
        elif isinstance(session, httpx.Client):
            merged_cookies = httpx.Cookies(session.cookies)
            merged_cookies.update(addcook)
            session.cookies.update(merged_cookies)
        else:
            log.error("出错了")
        # return session

    def update_session_headers(self, session, addhead=None):
        assert isinstance(addhead, dict)
        session.headers.update(addhead)
        return session

    def _get_session_like_dict(self, session, key):
        assert isinstance(key, str)
        ck = self.get_session_cookies(session)
        return self._get_sessioncookies_like_dicy(ck, key)

    def _get_sessioncookies_like_dicy(self, ck, key):
        assert isinstance(key, str)
        if isinstance(ck, requests.cookies.RequestsCookieJar):
            d = ck.get_dict()
            try:
                value = d[key]
            except:
                value = ck.get(key)
        elif isinstance(ck, httpx.Cookies):
            try:
                value = ck[key]
            except:
                value = ck.get(key)
        else:
            log.error("出错了")
            value = None
        return value

    def get_ck(self, session, key):
        ## 这里 session 可以是 session 对象 或者 Cookies 对象
        if isinstance(session, requests.sessions.Session) or isinstance(session, httpx.Client):
            return self._get_session_like_dict(session, key)
        elif isinstance(session, requests.cookies.RequestsCookieJar) or isinstance(session, httpx.Cookies):
            return self._get_sessioncookies_like_dicy(session, key)
        else:
            log.error("有问题")
            return None

    def cookie2dict(self, session):
        ## 这里 session 可以是 session 对象 或者 Cookies 对象
        if isinstance(session, requests.sessions.Session):
            cookie_dict = session.cookies.get_dict()
            return cookie_dict
        elif isinstance(session, requests.cookies.RequestsCookieJar):
            cookie_dict = session.get_dict()
            return cookie_dict

        elif isinstance(session, httpx.Client):
            ck = session.cookies
            cookies = ck.__dict__.get("jar", [])
            cookie_dict = {cookie.name: cookie.value for cookie in cookies}
            return cookie_dict
        elif isinstance(session, httpx.Cookies):
            cookies = session.__dict__.get("jar", [])
            cookie_dict = {cookie.name: cookie.value for cookie in cookies}
            return cookie_dict
        else:
            log.error("有问题")
            cookie_dict = None
            return cookie_dict


class SessionInitializer:
    def __init__(self, uid, **kwargs):
        self.uid = uid
        self.custom = CustomSession(**kwargs)
        self.session = self.custom.get_new_session(userequests=True, verbose=False)
        # self.session = self.custom.get_new_session(userequests=False, verbose=False)
        self.username, self.password, self.prodata = self._get_user_credentials()

    def _get_user_credentials(self):
        m1 = ProjectInfoGetter()
        yamldata = read_yaml_file(m1.in_userinfo_file)
        assert len(yamldata) >= 1, "请在 userinfo.yaml 文件中输入账号和密码"
        userid = yamldata[f"user{self.uid}"]
        username = userid["username"]
        password = userid["password"]
        prodata = ProjectInfoGetter(username)
        log.warning(f"当前选择的是第 {self.uid} 账号, 账号用户名 {username}")
        return username, password, prodata

    def initialize_session(self):
        log.warning(f"使用代理: {self.session.proxies}" if self.session.proxies else "没有使用代理")
        log.info("============开始登录, 准备获取 cookie =====================")
        try:
            current_path = os.path.dirname(os.path.realpath(__file__))
        except:
            current_path = os.getcwd()
        log.info(f"当前文件的路径: {os.path.abspath(current_path)}")

        return self.session, self.custom, self.prodata, self.uid, self.username, self.password


Headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
}


__all__ = ["CustomSession", "SessionInitializer"]
