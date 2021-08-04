#!/usr/bin/python3
# -*- coding: utf-8 -*-

from cmcc import CMCC
from hkpic import HKPIC
import sys
import json
from common import weixin_send_msg, save_log, today_in_log, get_running_path
import time
from config import HKpicConfig
from bs4 import BeautifulSoup


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit()

    sessionid = sys.argv[1]
    jsonValue = json.loads(sys.argv[2])
    openid = jsonValue['WeiXinOpenID']

    # 广东移动App签到
    if not today_in_log():
        save_log(time.strftime("%Y-%m-%d", time.localtime()))
        cmccValue = jsonValue['CMCC']
        cmcc = CMCC(sessionid, cmccValue)
        cmcc.runAction()
        weixin_send_msg('\n'.join(cmcc.weixin), openid)
        save_log(cmcc.weixin)

    # 比思签到+赚取每日金币
    hkpicValue = jsonValue['HKPIC']
    hkpic = HKPIC(hkpicValue)
    print('------------- 比思签到 -------------')
    hkpic.runAction()
    print('------------- 比思签到完成 -------------')
