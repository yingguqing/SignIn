#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 配置文件


from common import save_values, valueForKey, load_values, local_time
from time import time, sleep
from enum import Enum, auto
from loginfo import PrintLog, PrintType


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

    def __init__(self, log: PrintLog, mark, username):
        super().__init__(log)
        self.key = f'HKPIC_CONFIG_{mark}'
        self.username = username
        date = str(local_time().date())
        dic = load_values(self.key, '', {})
        self.money = valueForKey(dic, 'money', 0)
        self.index = valueForKey(dic, 'index', -1)
        self.date = valueForKey(dic, 'date')
        self.user_zone_url = valueForKey(dic, 'user_zone_url', '')
        if self.date != date:
            # 如果数据不是今天的，就不读取，使用默认值
            self.date = date
            dic = {}
        # 上一次发表评论的时间，因为一个小时内只能发10条
        self.last_reply_time = valueForKey(dic, 'last_reply_time', 0)
        # 发表评论次数（1小时内限发10次，有奖次数为15次）
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
        self.max_reply_times = 10
        # 评论最大失败次数
        self.max_reply_fail_times = 10
        if self.reply_times > 5:
            self.max_reply_times = 15
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

    def canReply(self):
        '''
        是否需要发表评论
        '''
        reply = self.reply_times < self.max_reply_times and self.max_reply_fail_times > 0
        if reply and self.reply_times == 10:
            # 一个小时内，同一个账号，发表评论数最大为10
            return time() - self.last_reply_time > 3600
        return reply

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
            'money': self.money,
            'date': self.date,
            'is_visit_other_zone': self.is_visit_other_zone,
            'reply_times': self.reply_times,
            'is_leave_message': self.is_leave_message,
            'is_record': self.is_record,
            'journal_times': self.journal_times,
            'share_times': self.share_times,
            'last_reply_time': self.last_reply_time
        }
        if self.user_zone_url:
            values['user_zone_url'] = self.user_zone_url

        if self.index >= 0:
            values['index'] = self.index

        return values
