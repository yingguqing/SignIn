#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 配置文件


from common import save_values, valueForKey, load_values, local_time, print_sleep, print_error
import time
from enum import Enum, auto


class Config:
    key = ''

    def __init__(self):
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

    # 保存公共配置数据
    def savePublicConfig(self):
        if not self.public_config:
            return
        save_values('PUBLIC_CONFIG', '', self.public_config)


# 比思发表类型
class PicType(Enum):
    Reply = auto()
    LeaveMessage = auto()
    Record = auto()
    Journal = auto()
    Share = auto()

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
        else:
            return '未知'

    # 最大休息时间，肯定会成功的休息时间，比正常休息时长多
    def maxSleepTime(self):
        if self is PicType.Reply:
            return 60
        elif self is PicType.LeaveMessage:
            return 60
        elif self is PicType.Record:
            return 100
        elif self is PicType.Journal:
            return 100
        elif self is PicType.Share:
            return 60
        else:
            return 0


class HKpicConfig(Config):

    def __init__(self, mark):
        super().__init__()
        self.key = f'HKPIC_CONFIG_{mark}'
        date = str(local_time().date())
        dic = load_values(self.key, '', {})
        self.money = valueForKey(dic, 'money', 0)
        self.date = valueForKey(dic, 'date')
        # 发表评论后的休息时间
        self.reply_sleep_time = valueForKey(self.public_config, 'reply_sleep_time', PicType.Reply.maxSleepTime())
        # 发表留言后的休息时间
        self.leave_message_sleep_time = valueForKey(self.public_config, 'leave_message_sleep_time', PicType.LeaveMessage.maxSleepTime())
        # 发表记录后的休息时间
        self.record_sleep_time = valueForKey(self.public_config, 'record_sleep_time', PicType.Record.maxSleepTime())
        # 发表日志后的休息时间
        self.journal_sleep_time = valueForKey(self.public_config, 'journal_sleep_time', PicType.Journal.maxSleepTime()) - 1
        # 发表分享后的休息时间
        self.share_sleep_time = valueForKey(self.public_config, 'share_sleep_time', PicType.Share.maxSleepTime()) - 1
        self.savePublicConfig()
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
        if self.reply_times > 5:
            self.max_reply_times = 15
        # 发表日志的最大次数
        self.max_journal_times = 3
        #  最大分享次数
        self.max_share_times = 3

    # 是否需要发表评论
    def canReply(self):
        reply = self.reply_times < self.max_reply_times
        if reply and self.reply_times == 10:
            # 一个小时内，同一个账号，发表评论数最大为10
            return time.time() - self.last_reply_time > 3600
        return reply

    # 是否需要发表日志
    def canJournal(self):
        return self.journal_times < self.max_journal_times

    # 是否需要发表分享
    def canShare(self):
        return self.share_times < self.max_share_times

    # 按类型自动休息
    def sleep(self, type):
        if not isinstance(type, PicType):
            return

        if type is PicType.Reply:
            print_sleep(self.reply_sleep_time)
        elif type is PicType.LeaveMessage:
            print_sleep(self.leave_message_sleep_time)
        elif type is PicType.Record:
            print_sleep(self.record_sleep_time)
        elif type is PicType.Journal:
            print_sleep(self.journal_sleep_time)
        elif type is PicType.Share:
            print_sleep(self.share_sleep_time)

    # 增加休息时长
    def increaseSleepTime(self, type, is_sleep: bool = True):
        if type is PicType.Reply:
            self.reply_sleep_time += 1
            self.reply_sleep_time = min(self.reply_sleep_time, type.maxSleepTime())
            is_max = self.reply_sleep_time == type.maxSleepTime()
            print_error(f'{str(type)} 休息时间延长到{self.reply_sleep_time}秒')
        elif type is PicType.LeaveMessage:
            self.leave_message_sleep_time += 1
            self.leave_message_sleep_time = min(self.leave_message_sleep_time, type.maxSleepTime())
            is_max = self.leave_message_sleep_time == type.maxSleepTime()
            print_error(f'{str(type)} 休息时间延长到{self.leave_message_sleep_time}秒')
        elif type is PicType.Record:
            self.record_sleep_time += 1
            self.record_sleep_time = min(self.record_sleep_time, type.maxSleepTime())
            is_max = self.record_sleep_time == type.maxSleepTime()
            print_error(f'{str(type)} 休息时间延长到{self.record_sleep_time}秒')
        elif type is PicType.Journal:
            self.journal_sleep_time += 2
            self.journal_sleep_time = min(self.journal_sleep_time, type.maxSleepTime())
            is_max = self.journal_sleep_time == type.maxSleepTime()
            print_error(f'{str(type)} 休息时间延长到{self.journal_sleep_time}秒')
        elif type is PicType.Share:
            self.share_sleep_time += 1
            self.share_sleep_time = min(self.share_sleep_time, type.maxSleepTime())
            is_max = self.share_sleep_time == type.maxSleepTime()
            print_error(f'{str(type)} 休息时间延长到{self.share_sleep_time}秒')
        else:
            is_max = False

        self.savePublicConfig()

        if is_sleep:
            self.sleep(type)

        return is_max

    def configValue(self):
        values = {
            'money': self.money,
            'date': self.date,
            'reply_times': self.reply_times,
            'is_visit_other_zone': self.is_visit_other_zone,
            'is_leave_message': self.is_leave_message,
            'is_record': self.is_record,
            'journal_times': self.journal_times,
            'share_times': self.share_times,
            'last_reply_time': self.last_reply_time
        }
        return values

    def savePublicConfig(self):
        self.public_config['reply_sleep_time'] = self.reply_sleep_time
        self.public_config['leave_message_sleep_time'] = self.leave_message_sleep_time
        self.public_config['record_sleep_time'] = self.record_sleep_time
        self.public_config['journal_sleep_time'] = self.journal_sleep_time
        self.public_config['share_sleep_time'] = self.share_sleep_time
        super().savePublicConfig()
