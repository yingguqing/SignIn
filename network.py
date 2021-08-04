#!/usr/bin/python3
# -*- coding: utf-8 -*-


import requests
from urllib.parse import urljoin
import time
from common import valueForKey


class Network:

    # 准备微信推送的消息
    weixin = []

    def __init__(self, jsonValue):
        self.host = valueForKey(jsonValue, 'host')
        self.verify = True
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

        url_headers['Cookie'] = self.cookies if self.cookies else ''

        requests.packages.urllib3.disable_warnings()
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
        try:
            # requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
            if post:
                params = self.format(params, url_headers)
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

        query = self.paramsString(params)
        return f'{url}?{query}'
    
    # 字典参数转成a=1&b=2
    def paramsString(self, params):
        result = ''
        if type(params) is dict:
            p = []
            for (key, value) in params.items():
                p.append('{key}={value}'.format(key=key, value=value))
            result = '&'.join(p)
        else:
            result = params
        return result

    def format(self, data, headers):
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

        #从headers中提取boundary信息
        if "Content-Type" in headers:
            fd_val = str(headers["Content-Type"])
            if "boundary" in fd_val:
                fd_val = fd_val.split(";")[1].strip()
                boundary = fd_val.split("=")[1].strip()

        if not boundary:
            return data

        #form-data格式定式
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
