#!/usr/bin/python3
# -*- coding: utf-8 -*-

from typing import Text
import requests
from urllib.parse import urljoin
from common import valueForKey
import time

# 整个程序的开始时间
StartTime = time.time()
# 最大执行时长(单位：秒)
MaxRunTime = 3600


class Network:

    # 准备微信推送的消息
    weixin = []

    def __init__(self, jsonValue):
        self.host = valueForKey(jsonValue, 'host')
        self.verify = True
        self.isTimeOut = False
        # 网络请求所要用到的cookie
        self.cookies = ''
        self.headers = {
            'Accept-Language': 'zh-cn',
            'Accept': 'application/json, text/plain, */*',
            'Origin': self.host,
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GDMobile/8.0.4',
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }

    def request(self, url, params=None, headers=None, post=True, is_save_cookies=True):
        if time.time() - StartTime >= MaxRunTime:
            self.isTimeOut = True
            raise RuntimeError(f'运行超过{MaxRunTime}秒')

        url_headers = self.headers
        # 合并请求头
        if headers is not None:
            url_headers = {**url_headers, **headers}

        url_headers['Cookie'] = self.cookies if self.cookies else ''

        requests.packages.urllib3.disable_warnings()
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
        try:
            if post:
                params = self.formatBoundary(params, url_headers)
                res = requests.post(url=url, data=params, headers=url_headers, verify=self.verify)
            else:
                res = requests.get(url=url, headers=url_headers, verify=self.verify)

            res.encoding = 'utf-8'

            # 保存cookie
            if is_save_cookies:
                self.response_cookies(res.cookies)

            try:
                return res.json()
            except ValueError:
                return res.text
            finally:
                res.close()

        except AttributeError as e:
            print(e)
            pass
        except requests.exceptions.ConnectionError:
            return '域名不通'

    # 保存cookie，子类重写
    def response_cookies(self, cookies):
        pass

    # 请求的url补全
    def encapsulateURL(self, api, params=None, host=None):
        host = self.host if not host else host

        if api.startswith(host):
            url = api
        else:
            url = urljoin(host, api)

        if not params:
            return url

        query = self.paramsString(params)
        return f'{url}?{query}'

    # 字典参数转成a=1&b=2
    def paramsString(self, params):
        result = ''
        if params:
            if type(params) is dict:
                p = list(map(lambda key: f'{key}={params[key]}', params.keys()))
                result = '&'.join(p)
            else:
                result = params
        return result

    # 设置请求的referer，自动添加域名
    def refererURL(self, referer):
        if referer.startswith(self.host):
            url = referer
        else:
            url = urljoin(self.host, referer)
        self.headers['Referer'] = url
        return url

    def formatBoundary(self, data, headers):
        """
        form data
        :param: data:  {"req":{"cno":"18990876","flag":"Y"},"ts":1,"sig":1,"v": 2.0}
        :param: boundary: "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        :param: headers: 包含boundary的头信息；如果boundary与headers同时存在以headers为准
        :return: str
        :rtype: str
        """

        if type(data) is str:
            return data

        boundary = ''

        # 从headers中提取boundary信息
        if "Content-Type" in headers:
            fd_val = str(headers["Content-Type"])
            if "boundary" in fd_val:
                fd_val = fd_val.split(";")[1].strip()
                boundary = fd_val.split("=")[1].strip()

        if not boundary:
            return data

        # form-data格式定式
        jion_str = '--{}\r\nContent-Disposition: form-data; name="{}"\r\n\r\n{}\r\n'
        end_str = "--{}--".format(boundary)
        args_str = ""

        if not isinstance(data, dict):
            return data

        for key, value in data.items():
            args_str = args_str + jion_str.format(boundary, key, value)

        args_str = args_str + end_str.format(boundary)
        args_str = args_str.replace("\'", "\"")
        return args_str.encode('utf-8')
