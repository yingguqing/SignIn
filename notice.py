#!/usr/bin/python3
# -*- coding: utf-8 -*-


from common import valueForKey
from urllib.parse import quote
import requests
from threading import Lock


class Notice:

    '''
    将消息通过Bark通知到手机
    '''

    def __init__(self, jsonValue):
        self.noticeKey = valueForKey(jsonValue, 'noticeKey')
        self.noticeIcon = valueForKey(jsonValue, 'noticeIcon')
        self.groupName = valueForKey(jsonValue, 'groupName')
        self.lock = Lock()
        # 一次发送的消息列表
        self.noticeList = []

    def sendNotice(self, text: str, title: str = '', icon: str = '', group: str = ''):
        '''
        发送一条手机通知信息

        参数:
        title:通知标题(可以为空)
        text:通知内容
        icon:通知图标
        group:消息分组
        '''
        if not self.noticeKey or not text:
            return

        self.lock.acquire()
        url = f'https://api.day.app/{self.noticeKey}/'
        path = []
        # 加入标题
        if title:
            path.append(quote(title, 'utf-8'))

        # 加入内容
        path.append(quote(text, 'utf-8'))
        url += '/'.join(path)

        query = []
        # 通知图标
        if icon:
            query.append(f'icon={icon}')

        # 消息分组
        if group:
            query.append(f'group={group}')

        if query:
            url += ('?' + '&'.join(query))

        res = requests.get(url=url)
        res.encoding = 'utf-8'
        try:
            result = res.json()
            code = result['code']
            if not code or code != 200:
                print(res.text)
        except ValueError:
            print(res.text)
        finally:
            res.close()
            self.lock.release()

    def addNotice(self, text: str, index: int = -1):
        '''
        往通知列表中插入一条
        参数:
        text:通知内容
        index:插入位置（小于0表示添加到末尾）
        '''
        self.lock.acquire()
        if not index or index < 0 or index > len(self.noticeList):
            self.noticeList.append(text)
        else:
            self.noticeList.insert(index, text)
        self.lock.release()

    def sendAllNotice(self, title: str):
        '''
        将通知列表中的消息全部发送
        参数:
        title:通知标题
        '''
        if not self.noticeKey or not self.noticeList:
            return

        # 把列表中的消息拼接
        text = '\n'.join(self.noticeList)

        self.sendNotice(text, title, self.noticeIcon, self.groupName)
