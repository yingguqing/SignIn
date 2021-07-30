#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 比思每日签到

import json
from network import Network
from common import load_cookies, print_sleep, save_cookies, save_readme
from bs4 import BeautifulSoup
import re
import base64
from urllib.parse import quote
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
        self.cookie_dit = load_cookies('HKPIC', self.xor, {})
        self.response_cookies({})
        # 别人空间地址
        self.user_href = ''
        # 发表评论次数（1小时内限发10次，有奖次数为15次）
        self.reply_times = 0
        # 本次最大评论次数
        self.max_reply_times = 15
        # 自己的空间地址
        self.my_zone_url = ''
        # 我的金币
        self.my_money = 0
        # 发表评论等所要用的
        self.formhash = ''
        # 是否留言
        self.is_leave_message = True
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
            'Referer': self.fullURL('plugin.php?id=k_pwchangetip:tip')
        }
        self.comments = ["走过了年少，脚起了水泡。", "人生自古谁无死，啊个拉屎不用纸！", "如果跟导师讲不清楚，那么就把他搞胡涂吧！",
                         "不要在一棵树上吊死，在附近几棵树上多试试死几次。", "老天，你让夏天和冬天同房了吧？生出这鬼天气！",
                         "恋爱就是无数个饭局，结婚就是一个饭局。", "如果回帖是一种美德，那我早就成为圣人了！", "男人靠的住，母猪能上树！",
                         "天塌下来你顶着，我垫着！", "美女未抱身先走，常使色狼泪满襟。", "穿别人的鞋，走自己的路，让他们找去吧。",
                         "怀揣两块，胸怀500万！", "鸳鸳相抱何时了，鸯在一边看热闹。", "丑，但是丑的特别，也就是特别的丑！",
                         "自从我变成了狗屎，就再也没有人踩在我头上了。", "我怀疑楼主用的是金山快译且额外附带了中对中翻译。",
                         "流氓不可怕，就怕流氓有文化。", "听君一席话，省我十本书！", "如果有一双眼睛陪我一同哭泣，就值得我为生命受苦。",
                         "人生重要的不是所站的位置，而是所朝的方向！", "内练一口气，外练一口屁。", "找不到恐龙，就用蜥蜴顶。", 
                         "女，喜甜食，甚胖！该女有一癖好：痛恨蚂蚁，见必杀之。问其故曰：这小东西，那么爱吃甜食，腰还那么细！",
                         "不在放荡中变坏，就在沉默中变态！", "只要不下流，我们就是主流！", "月经不仅仅是女人的痛苦，也是男人的痛苦。",
                         "佛曰，色即是空，空即是色！今晚，偶想空一下。","勿以坑小而不灌，勿以坑大而灌之。", "读书读到抽筋处，文思方能如尿崩！",
                         "睡眠是一门艺术——谁也无法阻挡我追求艺术的脚步！", "人生不能像做菜、把所有的料都准备好才下锅！","锻炼肌肉，防止挨揍！", 
                         "我妈常说，我们家要是没有电话就不会这么穷。", "我不在江湖，但江湖中有我的传说。", "我喜欢孩子，更喜欢造孩子的过程！",
                         "时间永远是旁观者，所有的过程和结果，都需要我们自己承担。", "其实我是一个天才，可惜天妒英才！", "站的更高，尿的更远。",
                         "漏洞与补丁齐飞，蓝屏共死机一色！", "比我有才的都没我帅，比我帅的都没我有才！", "我身在江湖，江湖里却没有我得传说。",
                         "有来有往，你帮我挖坑，我买一送一，填埋加烧纸。", "所有的男人生来平等，结婚的除外。", "不在课堂上沉睡，就在酒桌上埋醉。",
                         "只有假货是真的，别的都是假的！", "男人有冲动可能是爱你，也可能是不爱，但没有冲动肯定是不爱！", "我在马路边丢了一分钱！",
                         "商女不知亡国恨、妓女不懂婚外情。", "脱了衣服我是禽兽，穿上衣服我是衣冠禽兽！", "你的丑和你的脸没有关系。",
                         "路边的野花不要，踩。", "长得真有创意，活得真有勇气！",  "走自己的路，让别人打车去吧。", "如果恐龙是人，那人是什么？"
                         "男人与女人，终究也只是欲望的动物吧！真的可以因为爱而结合吗？对不起，我也不知道。","有事秘书干，没事干秘书！",
                         "关羽五绺长髯，风度翩翩，手提青龙偃月刀，江湖人送绰号——刀郎。", "解释就系掩饰，掩饰等于无出色，无出色不如回家休息！",
                         "俺从不写措字，但俺写通假字！", "生我之前谁是我，生我之后我是谁？", "我靠！看来医生是都疯了！要不怎么让他出院了！",
                         "勃起不是万能的，但不能勃起却是万万都不能的！", "沒有激情的亲吻，哪來床上的翻滾？", "做爱做的事，交配交的人。",
                         "有时候，你必须跌到你从未经历的谷底，才能再次站在你从未到达的高峰。", "避孕的效果：不成功，便成“人”。",
                         "与时俱进，你我共赴高潮！", "恐龙说：“遇到色狼，不慌不忙；遇到禽兽，慢慢享受。", "生，容易。活，容易。生活，不容易。",
                         "人家解释，我想，这世界上又要多我这一个疯子了。", "长大了娶唐僧做老公，能玩就玩一玩，不能玩就把他吃掉。",
                         "此地禁止大小便，违者没收工具。", "昨天，系花对我笑了一下，乐得我晚上直数羊，一只羊，两只羊，三只羊。",
                         "打破老婆终身制，实行小姨股份制。引入小姐竞争制，推广情人合同制。", "要是我灌水，就骂我“三个代表”没学好吧。"]

    # 保存cookie
    def response_cookies(self, cookies):
        self.cookie_dit = {**self.cookie_dit, **cookies}
        self.cookies = ''
        for key, value in self.cookie_dit.items():
            self.cookies += f'{key}={value};'
        save_cookies('HKPIC', self.xor, json.dumps(self.cookie_dit))

    # 开始入口
    def runAction(self, auto=True):
        if auto:
            print('------------- 比思签到 -------------')
            # 获取所有比思域名
            self.getHost()

        # 访问首页得到可用域名
        if not self.forum():
            print('没有可用域名')
            return

        if auto:
            print(f'域名:{self.host}')

        # 如果cookie失效，就自动登录
        if not self.is_login:
            if auto and self.login() :
                self.runAction(False)
            return
        elif auto:
            print('自动登录成功')

        if not self.formhash:
            print('formhash提取失败')
            print('------------- 比思签到完成 -------------')
            return

        # 签到
        if self.need_sign_in:
            self.signIn()
        else:
            print('今天已签到。')

        # 发表15次评论
        if self.reply_times < self.max_reply_times:
            print('开始评论。')
        self.forum_list(True)

        # 访问别人空间并留言
        self.visitUserZone()

        # 查询我的金币
        self.myMoney()
        save_readme([f'金钱：{self.my_money}'])

        # 删除自己空间留言所产生的动态
        self.delAllLeavMessageDynamic()
        print('------------- 比思签到完成 -------------')

    # 获取比思域名
    def getHost(self):
        print('获取比思域名')
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
        print('访问首页')
        self.host = ''
        for host in self.all_host:
            url = self.fullURL('forum.php', host)
            html = self.request(url, post=False)
            if html is not None and html.find('比思論壇') > -1:
                self.host = host
                self.headers['Origin'] = host
                self.headers['Referer'] = self.fullURL('plugin.php?id=k_pwchangetip:tip')
                soup = BeautifulSoup(html, 'html.parser')
                # 读取首页的用户名，如果存在，表示cookie还能用
                span = soup.find('a', title='訪問我的空間')
                if span:
                    # 提取自己的空间地址
                    self.my_zone_url = self.fullURL(span['href']) if span.has_attr('href') else ''
                    self.is_login = span.text == self.username
                    if self.is_login:
                        self.need_sign_in = html.find('簽到領獎!') > -1
                        # 提取formhash
                        span = soup.find('input', attrs={'name': 'formhash'})
                        if span and span.has_attr('value'):
                            self.formhash = span['value']
                return True
        return False

    # 登录
    def login(self):
        # 需要登录时，把cookie清空
        self.cookie_dit = {}
        self.cookies = ''
        api_param = 'mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
        url = self.encapsulateURL('member.php', api_param)
        params = f'fastloginfield=username&username={self.username}&password={self.password}&quickforward=yes&handlekey=ls'
        jsonString = self.request(url, params)
        tip = self.fullURL('plugin.php?id=k_pwchangetip:tip')
        result = jsonString.find(tip) > -1
        print('用户名登录成功' if result else f'登录失败\n{jsonString}')
        return result

    # 签到
    def signIn(self):
        api_param = 'id=dsu_paulsign:sign&operation=qiandao&infloat=1&sign_as=1&inajax=1'
        url = self.encapsulateURL('plugin.php', api_param)
        params = f'formhash={self.formhash}&qdxq=kx'
        html = self.request(url, params)
        pattern = re.compile(r'<div\s+class\s*=\s*"c"\s*>\W*(.*?)\W*<\s*/\s*div\s*>', re.S)
        items = re.findall(pattern, html)
        if items:
            print(items[0])
        else:
            print(f'签到失败\n{html}')

    # 版块帖子列表
    def forum_list(self, first_time=False):
        # 帖子较多的板块
        all = [2, 10, 11, 18, 20, 31, 42, 50, 79, 117, 123, 135, 142, 153, 239, 313, 398, 445, 454, 474, 776, 924]
        # 版块id
        fid = choice(all)
        # 页码
        page = randint(3, 10)
        api = f'forum-{fid}-{page}.html'
        url = self.fullURL(api)
        html = self.request(url, post=False)

        # 提取别人空间地址
        if not self.user_href:
            pattern = re.compile(r'"(space-uid-\d{5,}.html)"', re.S)
            items = re.findall(pattern, html)
            for item in items:
                if item != 'space-uid-562776.html':
                    self.user_href = self.fullURL(item)
                    break
        
        if self.reply_times >= self.max_reply_times:
            return

        if first_time:
            # 第一次时，先获取一下现有金币数
            self.myMoney(False)

        soup = BeautifulSoup(html, 'html.parser')
        # 提取板块下所有的帖子链接
        spans = soup.find_all('a', onclick='atarget(this)')
        # 板块内的贴子数(每个版块内最多回复3次)
        forum_reply_time = 0
        for span in spans:
            if not span.has_attr("style"):
                href = span['href']
                # 发表评论
                comment = choice(self.comments)
                # 从评论中随机取出一个进行发表
                if self.reply(comment, fid, href):
                    forum_reply_time += 1

                if forum_reply_time >= 3 or self.reply_times >= self.max_reply_times:
                    break

        # 评论数不够15条时，获取帖子下一页列表
        if self.reply_times < self.max_reply_times:
            self.forum_list()

    # 发表评论
    def reply(self, comment, fid, href):
        pattern = re.compile(r'\w*thread-(\d+)-\d+-\d+.\w+', re.S)
        items = re.findall(pattern, href)
        tid = items[0] if items else ''
        if not tid:
            print('帖子id不存在')
            return False

        url = self.fullURL(f'thread-{tid}-1-1.html')
        print(f'进入帖子：{url}')
        # 发表评论前的金币数
        money_history = self.my_money
        api_param = f'mod=post&action=reply&fid={fid}&tid={tid}&extra=page%3D1&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1'
        url = self.encapsulateURL('forum.php', api_param)
        timestamp = int(time.time())
        c = quote(comment, 'utf-8')
        params = f'message={c}&posttime={timestamp}&formhash={self.formhash}&usesig=1&subject=++'
        # 非常感謝，回復發佈成功
        html = self.request(url, params)
        if html.find('非常感謝，回復發佈成功') > -1:
            self.reply_times += 1
            print(f'第{self.reply_times}条：「{comment}」-> 發佈成功')
            # 评论有时间间隔限制
            if self.reply_times < self.max_reply_times:
                print_sleep(60)

            self.myMoney(False)
            if money_history == self.my_money:
                # 如果发表评论后，金币数不增加，就不再发表评论
                print('评论达到每日上限。不再发表评论。')
                self.reply_times = 99
            return True
        elif html.find('抱歉，您所在的用戶組每小時限制發回帖') > -1:
            print('评论数超过限制')
            self.reply_times = 9999
            return True
        else:
            print(comment)
            pattern = re.compile(r'\[CDATA\[(.*?)<', re.S)
            items = re.findall(pattern, html)
            print('\n'.join(items) if items else html)
            # 评论有时间间隔限制
            if self.reply_times < self.max_reply_times:
                print_sleep(60)
            return False

    # 从空间链接中获取用户id
    def getUid(self, href):
        pattern = re.compile(r'\w*space-uid-(\d+).\w+', re.S)
        items = re.findall(pattern, href)
        return items[0] if items else ''

    # 访问别人空间
    def visitUserZone(self):
        if self.user_href:
            url = self.user_href
            print(f'访问别人空间：{url}')
            self.request(url, post=False)
            uid = self.getUid(url)
            if uid:
                self.leavMessage(uid)
        else:
            print('别人空间地址为空')

    # 留言
    def leavMessage(self, uid):
        if not self.is_leave_message:
            return

        if not uid:
            print('他人id为空')
            return

        api_param = 'mod=spacecp&ac=comment&inajax=1'
        url = self.encapsulateURL('home.php', api_param)
        refer = quote(f'home.php?mod=space&uid={uid}', 'utf-8')
        message = quote('留个言，赚个金币。', 'utf-8')
        params = f'message={message}&refer={refer}&id={uid}&idtype=uid&commentsubmit=true&handlekey=commentwall_{uid}&formhash={self.formhash}'
        html = self.request(url, params)
        if html.find('操作成功') > -1:
            print('留言成功')
            pattern = re.compile(r'\{\s*\'cid\'\s*:\s*\'(\d+)\'\s*\}', re.S)
            items = re.findall(pattern, html)
            if items:
                cid = items[0]
                self.deleteMessage(cid)
        else:
            pattern = re.compile(r'\[CDATA\[(.*?)<', re.S)
            items = re.findall(pattern, html)
            print('\n'.join(items) if items else html)
            print('留言失败')

    # 删除留言
    def deleteMessage(self, cid):
        if not cid:
            return
        # 获取删除留言相关参数
        self.headers['Referer'] = self.user_href
        api_param = f'mod=spacecp&ac=comment&op=delete&cid={cid}&handlekey=delcommenthk_{cid}&infloat=yes&handlekey=c_{cid}_delete&inajax=1&ajaxtarget=fwin_content_c_{cid}_delete'
        url = self.encapsulateURL('home.php', api_param)
        self.request(url, post=False)

        # 请求删除留言
        api_param = f'mod=spacecp&ac=comment&op=delete&cid={cid}&inajax=1'
        url = self.encapsulateURL('home.php', api_param)
        refer = quote(self.user_href, 'utf-8')
        params = f'referer={refer}&deletesubmit=true&formhash={self.formhash}&handlekey=c_{cid}_delete'
        html = self.request(url, params)
        if html.find('操作成功') > -1:
            print('删除留言成功')
        else:
            pattern = re.compile(r'\[CDATA\[(.*?)<', re.S)
            items = re.findall(pattern, html)
            print('\n'.join(items) if items else html)
            print('删除留言失败')

    # 获取我的金币数
    def myMoney(self, is_print=True):
        if not self.my_zone_url:
            return
        html = self.request(self.my_zone_url, post=False)
        soup = BeautifulSoup(html, 'html.parser')
        is_money = False
        for string in soup.strings:
            flag = repr(string)
            if not is_money and flag.find('金錢') > -1:
                is_money = True
            elif is_money:
                try:
                    money = int(string)
                    self.my_money = money
                    if is_print:
                        print(f'金钱：{money}')
                    return
                except ValueError:
                    return

    # 删除自己空间留言所产生的动态
    def delAllLeavMessageDynamic(self):
        uid = self.getUid(self.my_zone_url)
        if not uid:
            return

        print('获取所有留言动态')
        api_params = f'mod=space&uid={uid}&do=home&view=me&from=space'
        url = self.encapsulateURL('home.php', api_params)
        
        html = self.request(url, post=False)
        pattern = re.compile(r'"home.php\?mod=spacecp&amp;ac=feed&amp;op=menu&amp;feedid=(\d+)"')
        feedids = re.findall(pattern, html)
        if feedids:
            print(f'共有{len(feedids)}条动态')
        else:
            print('没有动态需要删除')
            return
        
        for feedid in feedids:
            self.delLeavMessageDynamic(feedid, url)
    
    # 删除一条动态
    def delLeavMessageDynamic(self, feedid, referer):
        if not feedid or not referer:
            return

        # 获取删除动态相关参数
        self.headers['Referer'] = referer
        api_param = f'mod=spacecp&ac=feed&op=menu&feedid={feedid}&infloat=yes&handlekey=a_feed_menu_{feedid}&inajax=1&ajaxtarget=fwin_content_a_feed_menu_{feedid}'
        url = self.encapsulateURL('home.php', api_param)
        self.request(url, post=False)

        api_params = f'mod=spacecp&ac=feed&op=delete&feedid={feedid}&handlekey=a_feed_menu_{feedid}&inajax=1'
        url = self.encapsulateURL('home.php', api_params)
        referer = quote(url, 'utf-8')
        params = f'referer={referer}&feedsubmit=true&formhash={self.formhash}'
        html = self.request(url, params)
        if html.find('操作成功') > -1:
            print('删除动态成功')
        else:
            pattern = re.compile(r'\[CDATA\[(.*?)<', re.S)
            items = re.findall(pattern, html)
            print('\n'.join(items) if items else html)
            print('删除动态失败')