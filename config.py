#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 配置文件


from common import save_values, valueForKey, load_values
import json
import os
import time


class Config:
    key = ''

    # 配置参数封装成字典，子类实现
    def configValue(self):
        return None

    def save(self):
        if not self.key:
            return
        value = self.configValue()
        if value is None:
            return

        save_values(self.key, '', json.dumps(value))


class HKpicConfig(Config):

    def __init__(self, id):
        super().__init__()
        self.key = f'HKPIC_CONFIG_{id}'
        date = time.strftime("%Y-%m-%d", time.localtime())
        dic = load_values(self.key, '', {})
        self.money = valueForKey(dic, 'money', 0)
        self.date = valueForKey(dic, 'date')
        if self.date != date:
            # 如果数据不是今天的，就不读取，使用默认值
            self.date = date
            dic = {}
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
        # 发表日志失败的次数（3次内重试）
        self.journal_faild_times = 0
        # 发表分享失败的次数（3次内重试）
        self.share_faild_times = 0
        # 本次最大评论次数(有奖次数为15，小时内最大评论数为10)
        self.max_reply_times = 10
        if self.reply_times > 5:
            self.max_reply_times = 15
        # 发表日志的最大次数
        self.max_journal_times = 3
        #  最大分享次数
        self.max_share_times = 3

    def canReply(self):
        return self.reply_times < self.max_reply_times

    def canJournal(self):
        return self.journal_times < self.max_journal_times

    def canShare(self):
        return self.share_times < self.max_share_times

    def configValue(self):
        values = {
            'money': self.money,
            'date': self.date,
            'reply_times': self.reply_times,
            'is_visit_other_zone': self.is_visit_other_zone,
            'is_leave_message': self.is_leave_message,
            'is_record': self.is_record,
            'journal_times': self.journal_times,
            'share_times': self.share_times
        }
        return values
