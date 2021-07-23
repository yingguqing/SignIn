#!/usr/bin/python3
# -*- coding: utf-8 -*-

from network import Network
import sys
import json

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit()
    sessionid = sys.argv[1]
    jsonValue = json.loads(sys.argv[2])
    Network(sessionid, jsonValue).apiSignIn()
