#!/usr/bin/env python
#-8_coding:utf-8 -*-

import pWebSocket
import time

t = pWebSocket.run()

if t:
    for val in t:
        print val

while True:
    if not t[2].isAlive():
        break
    time.sleep(1)
    print 'ppp.py runrunrun'
