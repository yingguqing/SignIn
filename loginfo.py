#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 日志打印文件


from enum import Enum
import random
from common import get_running_path, local_time


class PrintType(Enum):
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

    # 根据类型，生成相应颜色的文字
    def text(self, log: str):
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

    def __init__(self, log: str, type: PrintType, title: str = '', logName: str = ''):
        self.log = log
        self.type = type
        self.title = title
        self.logName = logName

    # 保存日志到文件中
    def saveLogToText(self):
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
        title = f'{self.title}:' if self.title else ''
        print(f'{title}{self.type.text(self.log)}')


class PrintLog:

    def __init__(self, title: str = ''):
        self.__logs = []
        self.title = title
        self.isDebug = False
        self.logName = ''

    def setDebugAndLogFileName(self, name: str, isDebug: bool = False):
        self.isDebug = isDebug
        self.logName = name
        self.print('', PrintType.Normal)

    def __print(self, info: LogInfo):
        self.__logs.append(info)
        if not self.isDebug:
            return
        info.saveLogToText()
        info.print()

    # 打印日志
    def print(self, text, type: PrintType):
        if isinstance(text, list):
            [self.print(t, type) for t in text]
            for t in text:
                self.print(t, type)
        elif isinstance(text, str):
            info: LogInfo = LogInfo(text, type, self.title, self.logName)
            self.__print(info)

    # 清空所有日志
    def clear(self):
        self.__logs.clear()

    # 打印所有记录下来的日志
    def printAll(self):
        all = map(lambda log: log.type.text(log.log), self.__logs)
        if not all:
            return
        print('\n'.join(all))
        print('\n')
