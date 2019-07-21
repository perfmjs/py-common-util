# coding: utf-8 or # -*- coding: utf-8 -*-
import requests
import time
import traceback
from urllib.parse import urlparse

try:
    # 禁用安全请求警告
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print("WARN：禁用安全请求警告操作错误(InsecureRequestWarning import error)")


class RequestsUtils:

    def __init__(self, headers=None, referer="", timeout=(3.05, 5), proxies=[{}]):
        """
         支持动态切换代理(shadowsocks+polipo)
         e.g. proxies=[{},{"http":"http://127.0.0.1:1087","https":"http://127.0.0.1:1087"}，{"http":"http://127.0.0.1:1088","https":"http://127.0.0.1:1088"}]
        """
        if headers is None:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36",
                "X-Requested-With": "xmlHttpRequest",
                "Referer": referer,
                "Accept": "*/*",
                'Cache-Control': 'no-cache',
                'If-Modified-Since': '0'
            }
        from py_common_util.common.common_utils import CommonUtils
        if not isinstance(proxies, list):
            proxies = [proxies]
        self._proxies_num = len(proxies)
        self.proxies_iter = CommonUtils.cycle(proxies)
        self.sess = requests.Session()
        self.sess.proxies = next(self.proxies_iter)
        self.sess.verify = False
        self.headers = headers
        self.timeout = timeout
        self.cookies_jar = requests.cookies.RequestsCookieJar()

    def get(self, url, params=None, retry_count=0, retry_count_max=0, refresh_rate_in_second=0, hooks_exception_callback=None):
        """
        get请求, 异常请求则返回None
        :param url:
        :param params:
        :param retry_count:
        :param retry_count_max: 一般为proxies列表的长度减去1
        :param refresh_rate_in_second:
        :param hooks_exception_callback:
        :return:
        """
        try:
            if self.headers.get("Host") is None or len(self.headers.get("Host")) < 1:
                self.headers["Host"] = self.url_parse(url).hostname
            return self.sess.get(url, params=params, headers=self.headers, cookies=self.cookies_jar, timeout=self.timeout)
        except Exception as expt:
            if retry_count < retry_count_max:
                if 'Max retries exceeded with url' in traceback.format_exc():
                    print('出现Max retries exceeded with url异常，也许需要切换代理变量再重试(HTTP_PROXY,HTTPS_PROXY)！')
                    self.update_proxies()
                retry_count += 1
                print("GET URL[" + url + "]retry times:" + str(retry_count) + " of " + str(retry_count_max))
                if refresh_rate_in_second > 0:
                    time.sleep(refresh_rate_in_second)
                return self.get(url, params, retry_count, retry_count_max, refresh_rate_in_second, hooks_exception_callback)
            elif hooks_exception_callback:
                hooks_exception_callback(expt)
            else:
                # will return None
                traceback.print_exc()

    def post(self, url, data=None, retry_count=0, retry_count_max=0, refresh_rate_in_second=0, hooks_exception_callback=None):
        """
        post请求, 异常请求则返回None
        :param url:
        :param data:
        :param retry_count:
        :param retry_count_max: 一般为proxies列表的长度减去1
        :param refresh_rate_in_second:
        :param hooks_exception_callback:
        :return:
        """
        try:
            if self.headers.get("Host") is None or len(self.headers.get("Host")) < 1:
                self.headers["Host"] = self.url_parse(url).hostname
            return self.sess.post(url, data=data, headers=self.headers, cookies=self.cookies_jar, timeout=self.timeout)
        except Exception as expt:
            if retry_count < retry_count_max:
                if 'Max retries exceeded with url' in traceback.format_exc():
                    print('出现Max retries exceeded with url异常，也许需要切换代理变量再重试(HTTP_PROXY,HTTPS_PROXY)！')
                    self.update_proxies()
                retry_count += 1
                print("POST URL[" + url + "]retry times:" + str(retry_count) + " of " + str(retry_count_max))
                if refresh_rate_in_second > 0:
                    time.sleep(refresh_rate_in_second)
                return self.post(url, data, retry_count, retry_count_max, refresh_rate_in_second, hooks_exception_callback)
            elif hooks_exception_callback:
                hooks_exception_callback(expt)
            else:
                # will return None
                traceback.print_exc()

    def close(self):
        self.sess.close()

    def update_proxies(self):
        self.sess.proxies.update(next(self.proxies_iter))

    def get_proxies_num(self):
        return self._proxies_num

    def set_cookie_by_name(self, name, value, domain="", path="/"):
        self.cookies_jar.set(name, value, domain=domain, path=path)

    def remove_cookie_by_name(self, name, domain=None, path=None):
        """Unsets a cookie by name, by default over all domains and paths.

        Wraps CookieJar.clear(), is O(n).
        """
        clearables = []
        for cookie in self.cookies_jar:
            if cookie.name != name:
                continue
            if domain is not None and domain != cookie.domain:
                continue
            if path is not None and path != cookie.path:
                continue
            clearables.append((cookie.domain, cookie.path, cookie.name))

        for domain, path, name in clearables:
            self.cookies_jar.clear(domain, path, name)

    @staticmethod
    def url_parse(url):
        return urlparse(url)

    @staticmethod
    def domain_parse(url, globle_domain=False):
        domain = RequestsUtils.url_parse(url).hostname
        if not globle_domain:
            return domain
        else:
            split_at = domain.split(".")
            i = (0, 1)[globle_domain and len(split_at)>2]
            return ".".join(split_at[i:]).lower()

    @staticmethod
    def decode_content(req_content, encoding="utf-8"):
        return req_content.decode(encoding=encoding)


if __name__ == '__main__':
    def hooks_callback(expt):
        print("这是一个callback函数", expt)
        # raise expt
    url = "http://www.stackoverflow.com?1=2"
    base_url = RequestsUtils.domain_parse(url, True)
    print(base_url)
    parse = RequestsUtils.url_parse('https://api.github.com/events')
    print(parse.hostname)
    req = RequestsUtils(proxies=[{"http":"http://127.0.0.1:10871","https":"http://127.0.0.1:10871"},{"http":"http://127.0.0.1:10872","https":"http://127.0.0.1:10872"},{"http":"http://127.0.0.1:1087","https":"http://127.0.0.1:1087"}])
    # req = RequestsUtils(proxies={"http":"http://127.0.0.1:1087","https":"http://127.0.0.1:1087"})
    # req = RequestsUtils(proxies={})
    # r = req.get(url="https://api.github.com/events", retry_count_max=4)
    # print(r.json())
    # r = req.get(url="https://api.github.com/events", retry_count_max=4)
    # print(r.json())
    # r = req.get(url="https://api.github.com/events", retry_count_max=4)
    # print(r.json())
    try:
        r = req.get(url='https://www.facebook.com', retry_count_max=2, refresh_rate_in_second=3, hooks_exception_callback=hooks_callback)
        print("response=", r)
    except:
        print("主动抛出的异常:", traceback.format_exc())
    # r = req.get(url='https://kyfw.12306.cn/otn/leftTicket/queryZ',
    #           retry_count_max=1)
    # print(r.status_code)



