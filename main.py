#!/usr/bin/python3
# -*- coding: utf-8 -*-

from hkpic import HKPIC
from common import local_time, print_all, save_log
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
import sys
import json
import time


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit()

    ltime = local_time().strftime('%Y-%m-%d %H:%M:%S')
    print(f'\n当前北京时间：{ltime}\n')
    save_log(ltime)

    jsonValue = json.loads(sys.argv[1])
    # 读取并设置微信openid（功能暂时没用）
    # weixin_openid(jsonValue)

    hkpicValue = jsonValue['HKPIC']
    accounts = hkpicValue["accounts"]
    hkpicValue.pop('accounts')

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_list = []
        # 比思签到+赚取每日金币(多账号)
        for account in accounts:
            start = time.time()
            dic = {**hkpicValue, **account}
            hkpic = HKPIC(dic)
            hkpic.runAction()
            # future = executor.submit(hkpic.runAction)
            # future_list.append(future)

        # 设置线程的超时时间
        # wait(future_list, timeout=2400)

        # for future in as_completed(future_list):
        #     if future.result():
        #         print_all(future.result())
        #     else:
        #         print('没有执行结果')
