#!/usr/bin/python3
# -*- coding: utf-8 -*-

from cmcc import CMCC
from hkpic import HKPIC
import sys
import json
from common import weixin_send_msg, save_readme


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit()

    sessionid = sys.argv[1]
    jsonValue = json.loads(sys.argv[2])
    openid = jsonValue['WeiXinOpenID']

    # 广东移动App签到
    cmccValue = jsonValue['CMCC']
    cmcc = CMCC(sessionid, cmccValue)
    cmcc.runAction()
    weixin_send_msg('\n'.join(cmcc.weixin), openid)
    save_readme(cmcc.weixin)

    # 比思签到+赚取每日金币
    hkpicValue = jsonValue['HKPIC']
    hkpic = HKPIC(hkpicValue)
    hkpic.runAction()
