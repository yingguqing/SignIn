#!/usr/bin/python3
# -*- coding: utf-8 -*-


import requests
from urllib.parse import urljoin
import time
import platform


class Network:

    # 准备微信推送的消息
    weixin = [time.strftime("%Y-%m-%d", time.localtime())]

    def __init__(self, jsonValue):
        self.host = jsonValue['host']
        self.cookies = ''
        # 重试次数
        self.retime = 0
        self.headers = {
            'Accept-Language': 'zh-cn',
            'Accept': 'application/json, text/plain, */*',
            'Origin': self.host,
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GDMobile/8.0.4',
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
        }

    def request(self, url, params=None, headers=None, post=True, is_save_cookies=True):
        url_headers = self.headers
        # 合并请求头
        if headers is not None:
            url_headers = {**url_headers, **headers}

        if self.cookies:
            url_headers['Cookie'] = self.cookies

        requests.packages.urllib3.disable_warnings()
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
        try:
            if platform.system() != "Windows":
                requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'

            if post:
                res = requests.post(url=url, data=params, headers=url_headers, verify=False)
            else:
                res = requests.get(url=url, headers=url_headers, verify=False)

            res.encoding = 'utf-8'
            # 保存cookie
            if is_save_cookies:
                self.response_cookies(res.cookies)
            jsonValue = res.json()
            res.close()
            return jsonValue
        except AttributeError as e:
            print(e)
            pass
        except requests.exceptions.ConnectionError:
            return '域名不通'
        except ValueError:
            return res.text

    # 保存cookie，子类重写
    def response_cookies(self, cookies):
        pass

    # 补全链接
    def fullURL(self, href, host=None):
        host = self.host if not host else host
        if href.startswith(host):
            return href
        else:
            return urljoin(host, href)

    # 请求的url封装
    def encapsulateURL(self, api, params):
        url = urljoin(self.host, api)
        if not params:
            return url

        query = ''
        if type(params) is dict:
            p = []
            for (key, value) in params.items():
                p.append('{key}={value}'.format(key=key, value=value))
            query = '&'.join(p)
        elif type(params) is str:
            query = params

        return f'{url}?{query}'
