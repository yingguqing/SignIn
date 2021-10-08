#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 日志打印文件


from enum import Enum
import random
from common import get_running_path, local_time


class PrintType(Enum):
    '''
    日志类型
    '''
    # 正常打印，没有颜色
    Normal = 0
    # 34-37之间随机颜色
    Info = 1
    # 蓝色
    Blue = 34
    # 洋红
    Magenta = 35
    # 青色
    Cyan = 36
    # 白色
    White = 37
    # 警告
    Warn = 100
    # 成功
    Success = 200
    # 失败
    Error = 300

    def text(self, log: str):
        '''
        根据类型，生成相应颜色的文字
        '''
        show: str
        if self is PrintType.Error:
            show = '\033[7;30;31m{message}\033[0m'.format(message=log)
        elif self is PrintType.Success:
            show = '\033[7;30;32m{message}\033[0m'.format(message=log)
        elif self is PrintType.Warn:
            show = '\033[7;30;33m{message}\033[0m'.format(message=log)
        elif self is PrintType.Info:
            index = random.randint(34, 37)
            show = '\033[7;30;{i}m{message}\033[0m'.format(message=log, i=index)
        elif self.value >= 34 and self.value <= 37:
            show = '\033[7;30;{i}m{message}\033[0m'.format(message=log, i=self.value)
        else:
            show = log
        return show


class LogInfo:
    '''
    日志信息
    '''

    def __init__(self, log: str, type: PrintType, title: str = '', logName: str = ''):
        # 日志内容
        self.log = log
        # 日志类型
        self.type = type
        # 日志标题（非必须）
        self.title = title
        # 日志保存文件名（非必须）
        self.logName = logName

    def saveLogToText(self):
        '''
        保存日志到文件中
        '''
        if not self.logName:
            return

        ltime = local_time().strftime('%Y-%m-%d %H:%M:%S')
        path = get_running_path(self.logName)
        with open(path, 'a+', encoding='utf-8') as f:
            f.seek(0)
            f.write(f'{ltime}: {self.log}')
            f.write('\n')
            f.flush()

    def print(self):
        '''
        打印当前日志
        '''
        title = f'{self.title}:' if self.title else ''
        print(f'{title}{self.type.text(self.log)}')


# 打印日志
class PrintLog:

    def __init__(self, title: str = ''):
        self.__logs = []
        self.title = title
        self.isDebug = False
        self.logName = ''

    def setDebugAndLogFileName(self, name: str = ''):
        '''
        设置Debug模式和保存日志的文件名

        参数:
            name:文件名，为空时，不保存成文件
        '''
        self.isDebug = True
        self.logName = name
        self.print('', PrintType.Normal)

    def __print(self, info: LogInfo, isDebug: bool = False):
        '''
        记录日志列表，并打印日志

        参数:
            info:日志信息
            isDebug:是否是debug信息，debug信息只有在系统为debug模式下，才显示
        '''
        if not isDebug or self.isDebug:
            self.__logs.append(info)
        if not self.isDebug:
            return
        info.saveLogToText()
        info.print()

    # 打印日志
    def print(self, text, type: PrintType, isDebug: bool = False):
        '''
        打印日志

        参数:
            text:日志内容，可以是数组
            type:日志类型
            isDebug:是否是debug信息，debug信息只有在系统为debug模式下，才显示
        '''
        if isinstance(text, list):
            [self.print(t, type, isDebug) for t in text]
        elif isinstance(text, str):
            info: LogInfo = LogInfo(text, type, self.title, self.logName)
            self.__print(info, isDebug)

    def clear(self):
        '''
        清空所有日志
        '''
        self.__logs.clear()

    def printAll(self):
        '''
        打印所有记录下来的日志
        '''
        all = map(lambda log: log.type.text(log.log), self.__logs)

        if not all:
            return

        if self.isDebug:
            print('\n' * 5)

        print('\n'.join(all))
        print('\n')
