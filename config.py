#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 配置文件


from common import save_values, valueForKey, load_values, local_time
from time import sleep
from enum import Enum, auto
from loginfo import PrintLog, PrintType
from network import Network
import re


class Config:
    '''
    配置的基类
    '''
    key = ''

    def __init__(self, log: PrintLog):
        self.log = log
        self.total_sleep_time = 0
        self.public_config = load_values('PUBLIC_CONFIG', '', {})

    # 配置参数封装成字典，子类实现
    def configValue(self):
        return None

    def save(self):
        if not self.key:
            return
        value = self.configValue()
        if value is None:
            return

        save_values(self.key, '', value)

    def savePublicConfig(self):
        '''
        保存公共配置数据
        '''
        if not self.public_config:
            return
        save_values('PUBLIC_CONFIG', '', self.public_config)

    def print_sleep(self, secs):
        '''
        休息提示
        '''
        if secs is None:
            return

        total = self.total_sleep_time
        if secs <= 0:
            if secs == 0 and total:
                min = int(total/60)
                if min > 0:
                    consume = '%d分%.0f秒' % (min, total - min*60)
                else:
                    consume = f'{"%.0f" % total}秒'

                if total > 0:
                    self.log.print(f'休息：{consume}', PrintType.Magenta)
            return

        self.total_sleep_time += secs
        sleep(secs)


class PicType(Enum):
    '''
    比思发表类型
    '''
    Reply = auto()
    LeaveMessage = auto()
    Record = auto()
    Journal = auto()
    Share = auto()
    Other = auto()

    def __str__(self):
        if self is PicType.Reply:
            return '评论'
        elif self is PicType.LeaveMessage:
            return '留言'
        elif self is PicType.Record:
            return '记录'
        elif self is PicType.Journal:
            return '日志'
        elif self is PicType.Share:
            return '分享'
        elif self is PicType.Other:
            return '其他'
        else:
            return '未知'

    def sleepSec(self):
        '''
        比思各类型发表需要休息时间
        '''
        if self is PicType.Reply:
            return 51
        elif self is PicType.LeaveMessage:
            return 51
        elif self is PicType.Record:
            return 61
        elif self is PicType.Journal:
            return 51
        elif self is PicType.Share:
            return 3
        elif self is PicType.Other:
            return 2
        else:
            return 0


class HKpicConfig(Config):
    '''
    比思的配置类
    '''

    def __init__(self, log: PrintLog, mark, username, host):
        super().__init__(log)
        self.key = f'HKPIC_CONFIG_{mark}'
        self.otherUserId = 0
        self.username = username
        date = str(local_time().date())
        dic = load_values(self.key, '', {})
        money = valueForKey(dic, 'money', 0)
        self.money = money
        self.index = valueForKey(dic, 'index', 99)
        self.date = valueForKey(dic, 'date')
        self.userId = valueForKey(dic, 'user_id', 0)
        self.network = Network({'host': host})
        # 配置文件中保存的日期，是否是今天的
        self.isTodayDate = self.date == date
        if not self.isTodayDate:
            # 如果数据不是今天的，就不读取，使用默认值
            self.date = date
            dic = {}
        # 历史金币：第一次运行时，从网页获取，第二次运行时，从数据文件读取
        self.historyMoney = valueForKey(dic, 'history_money', money)
        # 发表评论次数（新手1小时内限发10次，有奖次数为15次）
        self.reply_times = valueForKey(dic, 'reply_times', 0)
        # 是否访问别人空间
        self.is_visit_other_zone = valueForKey(dic, 'is_visit_other_zone', True)
        # 是否留言
        self.is_leave_message = valueForKey(dic, 'is_leave_message', True)
        # 是否发表记录
        self.is_record = valueForKey(dic, 'is_record', True)
        # 发表日志次数
        self.journal_times = valueForKey(dic, 'journal_times', 0)
        #  分享次数
        self.share_times = valueForKey(dic, 'share_times', 0)
        # -----------以下是固定值------------------
        # 本次最大评论次数(有奖次数为15，小时内最大评论数为10)
        self.max_reply_times = 15
        # 评论最大失败次数
        self.max_reply_fail_times = 10
        # 发表日志的最大次数
        self.max_journal_times = 3
        # 最大分享次数
        self.max_share_times = 3
        # 留言的最大失败次数
        self.max_leave_msg_fail_times = 5
        # 发表记录的最大失败次数
        self.max_record_fail_times = 5
        # 发表日志的最大失败次数
        self.max_journal_fail_times = 5
        # 发表分享的最大失败次数
        self.max_share_fail_times = 5

    def reloadMoney(self):
        '''
        获取当前金钱数
        '''
        for _ in range(0, 5):
            money = self.userMoney(self.userId)
            if money > -1:
                isMore = self.money > money
                self.money = money
                return isMore
        return False

    def userMoney(self, userId):
        '''
        获取用户当前金钱数
        '''
        if userId < 9999:
            return -1
        url = self.network.encapsulateURL(f'space-uid-{userId}.html')
        html = self.network.request(url, post=False)
        pattern = re.compile(r'<li>金錢:\s*<a href=".*?">(\d+)</a>', re.I)
        items = re.findall(pattern, html)
        if items:
            money = int(items[0])
            return money
        else:
            return -1

    def moneyAddition(self, type: int):
        '''
        新增金钱。格式1：100 = 90 + 10,格式2：+10 -> 100
        '''
        if self.historyMoney < 0:
            return f'{self.money}'
        temp = self.money - self.historyMoney
        if temp <= 0:
            return f'{self.money}'
        if type == 1:
            return f'{self.money} = {self.historyMoney} + {temp}'
        elif type == 2:
            return f'+{temp} -> {self.money}'
        else:
            return f'{self.money}'

    def canReply(self):
        '''
        是否需要发表评论
        '''
        return self.reply_times < self.max_reply_times and self.max_reply_fail_times > 0

    def canJournal(self):
        '''
        是否需要发表日志
        '''
        return self.journal_times < self.max_journal_times and self.max_journal_fail_times > 0

    def canShare(self):
        '''
        是否需要发表分享
        '''
        return self.share_times < self.max_share_times and self.max_share_fail_times > 0

    def canLeaveMessage(self):
        '''
        是否需要留言
        '''
        return self.is_leave_message and self.max_leave_msg_fail_times > 0

    def canRecord(self):
        '''
        是否需要发表记录
        '''
        return self.is_record and self.max_record_fail_times > 0

    def sleep(self, type: PicType):
        '''
        根据类型休息
        '''
        if not isinstance(type, PicType):
            return
        sec: int = type.sleepSec()
        if sec <= 0:
            return
        self.print_sleep(sec)

    def configValue(self):
        '''
        配置信息生成字典，用于保存数据
        '''
        values = {
            'name': self.username,
            'user_id': self.userId,
            'date': self.date,
            'money': self.money,
            'is_visit_other_zone': self.is_visit_other_zone,
            'reply_times': self.reply_times,
            'is_leave_message': self.is_leave_message,
            'is_record': self.is_record,
            'journal_times': self.journal_times,
            'share_times': self.share_times
        }

        if self.money >= self.historyMoney:
            values["history_money"] = self.historyMoney

        if 0 < self.index < 99:
            values['index'] = self.index

        return values
