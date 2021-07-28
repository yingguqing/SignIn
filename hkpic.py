#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 比思每日签到

import json
from network import Network
from common import load_cookies, save_cookies, save_file
from bs4 import BeautifulSoup
import re
import base64
from urllib.parse import quote, urljoin
from random import choice, randint
import time


class HKPIC(Network):

    def __init__(self, jsonValue):
        super().__init__(jsonValue)
        self.all_host = [self.host]
        self.index = 0
        self.username = jsonValue['username']
        self.password = quote(jsonValue['password'])
        # 加密的key
        self.xor = jsonValue['xor']
        # cookie保存到本地的Key
        self.cookies_key = 'HKPIC'
        self.is_login = False
        # 需要签到
        self.need_sign_in = True
        self.cookies = ''
        # 读取本地cookie值
        self.cookie_dit = load_cookies(self.cookies_key, self.xor)
        self.response_cookies({})
        # 别人空间地址
        self.user_href = ''
        # 发表评论次数（1小时内限发10次，有奖次数为15次）
        # 评论有风险，可能会永久封号，禁止评论时，设置成99
        self.reply_times = 99
        self.headers = {
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Origin': 'bisi666.xyz',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GDMobile/8.0.4',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': self.host,
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': urljoin(self.host, 'plugin.php?id=k_pwchangetip:tip')
        }

    # 保存cookie
    def response_cookies(self, cookies):
        self.cookie_dit = {**self.cookie_dit, **cookies}
        self.cookies = ''
        for key, value in self.cookie_dit.items():
            self.cookies += f'{key}={value};'
        save_cookies(self.cookies_key, self.xor, json.dumps(self.cookie_dit))

    # 开始入口
    def runAction(self, auto=True):
        print('------------- 比思签到 -------------')
        # 获取所有比思域名
        self.getHost()

        # 访问首页得到可用域名
        if not self.forum():
            print('没有可用域名')
            return

        print(f'域名:{self.host}')

        # 如果cookie失效，就自动登录
        if not self.is_login:
            if self.login() and auto:
                self.runAction(False)
            else:
                print('登录失败')
            return
        else:
            print('自动登录成功')

        # 获取签到信息，并进行签到
        if self.need_sign_in:
            self.getSignInInfo()
        else:
            print('今天已签到。')

        # 发表15次评论
        print('开始评论。')
        self.forum_list()
        # 访问别人空间并留言
        self.visitUserZone()
        print('------------- 比思签到完成 -------------')

    # 获取比思域名
    def getHost(self):
        url = 'https://api.github.com/repos/hkpic-forum/hkpic/contents/README.md'

        req = self.request(url, post=False, is_save_cookies=False)
        if type(req) is dict and 'content' in req.keys():
            content = str(base64.b64decode(req['content']), 'utf-8')
            pattern = re.compile(r'\b(([\w-]+://?|www[.])[^\s()<>]+(?:[\w\d]+|([^[:punct:]\s]|/)))', re.S)
            all = re.findall(pattern, content)
            for h in all:
                if type(h) is tuple and h:
                    self.all_host.append(h[0])
        else:
            print('获取域名失败')

    # 访问首页得到可用域名
    def forum(self):
        self.host = ''
        for host in self.all_host:
            url = urljoin(host, 'forum.php')
            html = self.request(url, post=False)
            if html is not None and html.find('比思論壇') > -1:
                self.host = host
                self.headers['Origin'] = host
                self.headers['Referer'] = urljoin(host, 'plugin.php?id=k_pwchangetip:tip')
                soup = BeautifulSoup(html, 'html.parser')
                # 读取首页的用户名，如果存在，表示cookie还能用
                span = soup.find('a', title='訪問我的空間')
                if span:
                    self.is_login = span.text == self.username
                    if self.is_login:
                        self.need_sign_in = html.find('簽到領獎!') > -1
                return True
        return False

    # 登录
    def login(self):
        api_param = 'mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
        url = self.encapsulateURL('member.php', api_param)
        params = f'fastloginfield=username&username={self.username}&password={self.password}&quickforward=yes&handlekey=ls'
        jsonString = self.request(url, params)
        tip = urljoin(self.host, 'plugin.php?id=k_pwchangetip:tip')
        result = jsonString.find(tip) > -1
        print('用户名登录成功' if result else f'登录失败\n{jsonString}')
        return result

    # 获取签到信息
    def getSignInInfo(self):
        api_param = 'id=dsu_paulsign:sign&9bdaf884&infloat=yes&handlekey=dsu_paulsign&inajax=1&ajaxtarget=fwin_content_dsu_paulsign'
        url = self.encapsulateURL('plugin.php', api_param)
        html = self.request(url, post=False)
        if html.find('您今天已經簽到過了或者簽到時間還未開始') != -1:
            print('今天已签到')
        else:
            pattern = re.compile(r'<.*?name\s*=\s*"formhash"\s+value\s*=\s*"(\w+)"\s*>', re.S)
            items = re.findall(pattern, html)
            if items:
                self.signIn(items[0])
            else:
                print('获取签到formhash失败')

    # 签到
    def signIn(self, formhash):
        if formhash is None or len(formhash) == 0:
            print('签到formhash为空')
            return
        api_param = 'id=dsu_paulsign:sign&operation=qiandao&infloat=1&sign_as=1&inajax=1'
        url = self.encapsulateURL('plugin.php', api_param)
        params = f'formhash={formhash}&qdxq=kx'
        html = self.request(url, params)
        pattern = re.compile(r'<div\s+class\s*=\s*"c"\s*>\W*(.*?)\W*<\s*/\s*div\s*>', re.S)
        items = re.findall(pattern, html)
        if items:
            print(items[0])
        else:
            print(f'签到失败\n{html}')

    # 版块帖子列表
    def forum_list(self):
        # 所有能发表评论的板块
        all = [2, 5, 10, 11, 18, 20, 22, 25, 27, 28, 31, 33, 38, 39, 42, 46, 47, 49, 50, 57, 58, 59, 60, 61, 66, 67, 68, 75, 77, 78, 79, 83, 89, 91, 96, 98, 100,
               104, 105, 106, 110, 114, 115, 117, 118, 120, 121, 122, 123, 124, 126, 135, 140, 142, 150, 151, 153, 159, 163, 164, 165, 167, 182, 184, 194, 196, 198, 201,
               202, 208, 209, 210, 211, 212, 214, 232, 233, 234, 235, 236, 239, 244, 255, 256, 291, 299, 300, 304, 310, 313, 314, 338, 362, 370, 372, 373, 375, 376, 377,
               378, 381, 387, 390, 398, 401, 405, 417, 418, 419, 422, 423, 427, 433, 445, 447, 454, 474, 492, 628, 776, 924, 925]
        # 版块id
        block = choice(all)
        # 页码
        page = randint(3, 10)
        api = f'forum-{block}-{page}.html'
        url = urljoin(self.host, api)
        print(f'进入版块:{url}')
        html = self.request(url, post=False)
        # 获取最大页码
        pattern = re.compile(r'共\s+(\d*?)\s+頁', re.S)
        page_max = 0
        items = re.findall(pattern, html)
        for item in items:
            try:
                num = int(item)
                if num:
                    page_max = num
                    break
            except ValueError:
                pass

        # 请求页码超过最大页码时，不处理
        if page > page_max:
            self.forum_list()

        soup = BeautifulSoup(html, 'html.parser')
        # 提取板块下所有的帖子链接
        spans = soup.find_all('a', onclick='atarget(this)')
        for span in spans:
            if not span.has_attr("style"):
                href = span['href']
                # 读取帖子内容，发表评论
                self.thread(href)
                if self.reply_times >= 15:
                    return

        # 评论数不够15条时，获取帖子下一页列表
        if self.reply_times < 15:
            self.forum_list()

    # 读取帖子内容
    def thread(self, url):
        if not url.startswith(self.host):
            url = urljoin(self.host, url)
        html = self.request(url, post=False)
        soup = BeautifulSoup(html, 'html.parser')

        # 提取别人空间地址
        if not self.user_href:
            spans = soup.find_all('a', class_='xw1')
            for span in spans:
                if span.has_attr('href'):
                    href = span['href']
                    if href.startswith('space-uid-'):
                        self.user_href = href
                        break

        # 评论数够就不再发表
        if self.reply_times >= 15:
            return

        span = soup.find('input', attrs={'name': 'formhash'})
        if not span.has_attr('value'):
            print('获取评论的formhash参数失败')
            return
        formhash = span['value']
        comments = []
        spans = soup.find_all('td', class_='t_f')
        for span in spans:
            comment = span.text.replace('\n', '').replace('\r', '')
            count = len(comment)
            # 过滤过长和过短评论
            if count < 5 or count > 15:
                continue
            comments.append(comment)

        if not comments:
            return

        while True:
            comment = choice(comments)
            # 从评论中随机取出一个进行发表
            if self.reply(comment, formhash):
                break

    # 发表评论
    def reply(self, comment, formhash):
        api_param = 'mod=post&action=reply&fid=142&tid=7104505&extra=page%3D1&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1'
        url = self.encapsulateURL('forum.php', api_param)
        timestamp = int(time.time())
        c = quote(comment, 'utf-8')
        params = f'message={c}&posttime={timestamp}&formhash={formhash}&usesig=1&subject=++'
        # 非常感謝，回復發佈成功
        html = self.request(url, params)
        if html.find('非常感謝，回復發佈成功') > -1:
            self.reply_times += 1
            print(f'第{self.reply_times}条：「{comment}」->發佈成功')
            # 评论有时间间隔限制
            time.sleep(60)
            return True
        elif html.find('抱歉，您所在的用戶組每小時限制發回帖') > -1:
            print('回贴数超过限制')
            self.reply_times = 9999
            return True
        else:
            pattern = re.compile(r'\[CDATA\[(.*?)<', re.S)
            items = re.findall(pattern, html)
            print('\n'.join(items) if items else html)
            # 评论有时间间隔限制
            time.sleep(60)
            return False

    # 访问别人空间
    def visitUserZone(self):
        if self.user_href:
            if not self.user_href.startswith(self.host):
                url = urljoin(self.host, self.user_href)
            else:
                url = self.user_href

            print(f'访问别人空间：{url}')
            uid = ''
            formhash = ''
            pattern = re.compile(r'space-uid-(\d*?).html', re.S)
            items = re.findall(pattern, url)
            if items:
                uid = items[0]

            html = self.request(url, post=False)
            print(html)
            soup = BeautifulSoup(html, 'html.parser')
            span = soup.find('input', attrs={'name': 'formhash'})
            if span.has_attr('value'):
                formhash = span['value']
            if uid and formhash:
                self.leavMessage(uid, formhash)
        else:
            print('别人空间地址为空')

    # 留言
    def leavMessage(self, uid, formhash):
        api_param = 'mod=spacecp&ac=comment&inajax=1'
        url = self.encapsulateURL('home.php', api_param)
        refer = quote(f'home.php?mod=space&uid={uid}', 'utf-8')
        message = quote('留个言，赚个金币。', 'utf-8')
        params = f'message={message}&refer={refer}&id={uid}&idtype=uid&commentsubmit=true&handlekey=commentwall_{uid}&formhash={formhash}'
        html = self.request(url, params)
        print('留言成功' if html.find('操作成功') > -1 else '留言失败')
