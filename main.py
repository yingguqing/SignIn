#!/usr/bin/python3
# -*- coding: utf-8 -*-

from hkpic import HKPIC
import sys
import json
from common import save_log, today_in_log
import time
from datetime import datetime
from datetime import timedelta
from datetime import timezone


SHA_TZ = timezone(
    timedelta(hours=8),
    name='Asia/Shanghai',
)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit()

    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    beijing_now = utc_now.astimezone(SHA_TZ)
    print(beijing_now)

    jsonValue = json.loads(sys.argv[1])
    # sessionid = sys.argv[1]
    # openid = jsonValue['WeiXinOpenID']

    # 广东移动App签到
    if not today_in_log():
        save_log(beijing_now.date())
        # 移动app签到停用
        # cmccValue = jsonValue['CMCC']
        # cmcc = CMCC(sessionid, cmccValue)
        # cmcc.runAction()
        # weixin_send_msg('\n'.join(cmcc.weixin), openid)
        # save_log(cmcc.weixin)

    hkpicValue = jsonValue['HKPIC']
    accounts = hkpicValue["accounts"]
    hkpicValue.pop('accounts')
    # 比思签到+赚取每日金币(多账号)
    for account in accounts:
        dic = {**hkpicValue, **account}
        hkpic = HKPIC(dic)
        print(f'------------- {hkpic.username} 比思签到 -------------')
        hkpic.runAction()
        print(f'------------- {hkpic.username} 比思签到完成 -------------')
