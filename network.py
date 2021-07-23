#!/usr/bin/python3
# -*- coding: utf-8 -*-


import requests
import json
from urllib.parse import urljoin
from common import random_string, sign
import time
import os
import urllib3


class Network:

    def __init__(self, sessionid, jsonValue):
        self.host = 'https://gd.10086.cn'
        self.sessionid = sessionid
        self.id = jsonValue['id']
        self.ss = jsonValue['ss']
        self.openid = jsonValue['openid']
        self.ac_id = jsonValue['ac_id']
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

    def request(self, url, params, headers=None):
        url_headers = self.headers
        # 合并请求头
        if headers is not None:
            url_headers = {**url_headers, **headers}

        lv = int(time.time() * 1000)
        url_headers['Cookie'] = 'WT_FPC=id={id}:lv={lv}:ss={ss}'.format(id=self.id, lv=lv, ss=self.ss)
        requests.packages.urllib3.disable_warnings()
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
        try:
            requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
        except AttributeError:
            pass

        res = requests.post(url=url, data=params, headers=url_headers, verify=False)
        text = res.text
        print(text)
        try:
            jsonValue = json.loads(text)
            return jsonValue
        except ValueError:
            print(text)
            return None

    # 请求的url封装
    def encapsulateURL(self, api, params):
        url = urljoin(self.host, api)
        if params is not None:
            p = []
            for (key, value) in params.items():
                p.append('{key}={value}'.format(key=key, value=value))
            url += '?%s' % ('&'.join(p))
        return url

    # 请求参数封装
    def encapsulateParam(self, jsonData, sessionid):
        timestamp = int(time.time() * 1000)
        nonce = random_string()
        values = '{},{},{}'.format(sessionid, nonce, timestamp)
        _sign = sign(values)
        p = {
            'header': {
                'nonce': nonce,
                'timestamp': timestamp,
                'sign': _sign
            }
        }
        if jsonData is not None:
            p = {**p, **jsonData}

        params = 'reqJson=%s' % (json.dumps(p).replace('+', '%2B'))
        return params

    # 每日签到
    def apiSignIn(self):
        headers = {
            'Referer': 'https://gd.10086.cn/gmccapp/confactpage/signInNew/index.html?isApp=0&WT.ac_id=%s&session=%s' % (self.ac_id, self.sessionid),
        }
        params = self.encapsulateParam({'channel': ''}, self.sessionid)
        api_param = {
            'servicename': 'GMCCAPP_630_032_001_002',
            'sessionid': self.sessionid
        }
        url = self.encapsulateURL('gmccapp/confactapp/', api_param)
        jsonValue = self.request(url, params, headers)
        if 'result' in jsonValue.keys():
            result = jsonValue['result']
            desc = jsonValue['desc']
            loc_time = time.strftime("%Y-%m-%d", time.localtime())
            # 000:签到成功,111:已签到,001:系统繁忙,010:会话失效,100:录超时
            if result == '001':
                if self.retime < 10:
                    self.retime += 1
                    time.sleep(1)
                    self.apiSignIn()
                else:
                    self.sendmsg('{time}:签到失败,{desc}'.format(time=loc_time, desc=desc))
            else:
                self.sendmsg('{time}:{desc}'.format(time=loc_time, desc=desc))

    def get_access_token(self):
        """
        获取微信全局接口的凭证(默认有效期俩个小时)
        如果不每天请求次数过多, 通过设置缓存即可
        """
        result = requests.get(
            url="https://api.weixin.qq.com/cgi-bin/token",
            params={
                "grant_type": "client_credential",
                "appid": "wxc4ab4341d9a8577a",
                "secret": "e6c46e8cc24a95df1742ff8b25aaf36b",
            }
        ).json()

        if result.get("access_token"):
            access_token = result.get('access_token')
        else:
            access_token = None
        return access_token

    def sendmsg(self, msg):
        access_token = self.get_access_token()

        body = {
            "touser": self.openid,
            "msgtype": "text",
            "text": {
                "content": msg
            }
        }
        response = requests.post(
            url="https://api.weixin.qq.com/cgi-bin/message/custom/send",
            params={
                'access_token': access_token
            },
            data=bytes(json.dumps(body, ensure_ascii=False), encoding='utf-8')
        )
        # 这里可根据回执code进行判定是否发送成功(也可以根据code根据错误信息)
        result = response.json()
        print(result)
        fold = os.path.abspath('.')
        readMePath = os.path.join(fold, "README.md")
        with open(readMePath, 'a+') as f:
            f.seek(0)
            f.write('  \n')
            f.write(msg)
            f.write('  \n')
            f.write(json.dumps(result))
            f.flush()
