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
        # 比思签到+赚取每日金币(多账号)
        for account in accounts:
            dic = {**hkpicValue, **account}
            hkpic = HKPIC(dic, hkpicNotice)
            future = executor.submit(hkpic.runAction)
            future_list.append(future)
            sleep(2)

        for future in as_completed(future_list, timeout=3600):
            future.result()

        hkpicNotice.sendAllNotice('比思金币')
