#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 广东移动app每日签到

from network import Network
from common import random_string, sign, valueForKey
import time
import json


class CMCC(Network):

    def __init__(self, sessionid, jsonValue):
        super().__init__(jsonValue)
        self.sessionid = sessionid
        self.id = valueForKey(jsonValue, 'id')
        self.ac_id = valueForKey(jsonValue, 'ac_id')
        self.headers = {
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'Accept': 'application/json, text/plain, */*',
            'Origin': self.host,
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GDMobile/8.0.4',
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'DNT': '1',
            'sec-ch-ua-mobile': '?1',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty'
        }

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

    # 拼装自定义请求头
    def encapsulateHeader(self):
        # 拼装Cookie
        lv = int(time.time() * 1000)
        headers = {
            'Referer': 'https://gd.10086.cn/gmccapp/confactpage/signInNew/index.html?isApp=0&WT.ac_id=%s&session=%s' % (self.ac_id, self.sessionid),
            'Cookie': 'WT_FPC=id={id}:lv={lv}:ss={ss}; mobile=28985-22868-5494-39063'.format(id=self.id, lv=lv, ss=(lv + 2300))
        }
        return headers

    def run(self, api_param, params, title, max_time=5):
        headers = self.encapsulateHeader()
        url = self.encapsulateURL('gmccapp/confactapp/', api_param)
        jsonValue = self.request(url, params, headers, is_save_cookies=False)
        if not jsonValue:
            self.weixin.append('{title}：「返回数据为空」'.format(title=title))
            return

        print(jsonValue)
        desc = jsonValue
        if type(jsonValue) is not dict:
            jsonValue = {
                'result': '001',
                'desc': desc
            }
        allKeys = jsonValue.keys()
        if 'isDraw' in allKeys:
            isDraw = valueForKey(jsonValue, 'isDraw')
            desc = valueForKey(jsonValue, 'desc')
            if isDraw == '1':
                self.weixin.append('{title},{desc}'.format(title=title, desc=desc))
                return
        elif 'result' in allKeys:
            result = valueForKey(jsonValue, 'result')
            desc = valueForKey(jsonValue, 'desc')
            if 'isDraw' in allKeys and valueForKey(jsonValue, 'isDraw') == '1':
                # 已抽奖
                self.weixin.append('{title},{desc}'.format(title=title, desc=desc))
                return
            # 000:签到成功,111:已签到,001:系统繁忙,010:会话失效,100:登录超时
            if result == '001':
                if self.retime < max_time:
                    self.retime += 1
                    time.sleep(15)
                    self.run(api_param, params, title, max_time)
                else:
                    self.weixin.append('{title}：「{desc}」'.format(title=title, desc=desc))
            else:
                self.weixin.append('{title}：「{desc}」'.format(title=title, desc=desc))

    def runAction(self):
        self.apiSignIn()
        self.draw()

    # 每日签到
    def apiSignIn(self):
        params = self.encapsulateParam({'channel': ''}, self.sessionid)
        api_param = {
            'servicename': 'GMCCAPP_630_032_001_002',
            'sessionid': self.sessionid
        }
        self.run(api_param, params, '移动签到', max_time=10)

    # 累计三天后，抽奖(暂时不行，参数不对)
    def draw(self):
        params = self.encapsulateParam({'channel': '', 'entrance': ''}, self.sessionid)
        api_param = {
            'servicename': 'GMCCAPP_630_032_001_005',
            'sessionid': self.sessionid
        }
        self.run(api_param, params, '每日抽奖', max_time=5)
