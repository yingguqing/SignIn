#!/usr/bin/python3
# -*- coding: utf-8 -*-

from hkpic import HKPIC
from common import local_time
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
import sys
import json
from notice import Notice

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit()

    ltime = local_time().strftime('%Y-%m-%d %H:%M:%S')
    print(f'\n当前北京时间：{ltime}\n')

    jsonValue = json.loads(sys.argv[1])

    hkpicValue = jsonValue['HKPIC']
    # 配置比思通知类
    hkpicNotice = Notice(hkpicValue)
    accounts = hkpicValue["accounts"]
    hkpicValue.pop('accounts')

    with ThreadPoolExecutor() as executor:
        future_list = []
        hkpics = []
        otherUserId = 0
        # 比思签到+赚取每日金币(多账号)
        for account in accounts:
            dic = {**hkpicValue, **account}
            hkpic = HKPIC(dic, hkpicNotice)
            if otherUserId > 9999:
                hkpic.config.otherUserId = otherUserId
            otherUserId = hkpic.config.userId
            hkpics.append(hkpic)

        # 互换一下用户id来访问空间
        count = len(hkpics)
        if count > 1:
            hkpic = hkpics[0]
            hkpic.config.otherUserId = otherUserId

        for hkpic in hkpics:
            future = executor.submit(hkpic.runAction)
            future_list.append(future)
            sleep(2)

        for future in as_completed(future_list, timeout=3600):
            future.result()

        hkpicNotice.sendAllNotice('比思金币')
