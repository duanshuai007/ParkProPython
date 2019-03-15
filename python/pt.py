#!/usr/bin/env python
#-*- coding:utf-8 -*-

import pMysql as p

#string = 'À¶,Ô¥D15888,60'
#r = p.mysql_update_canparktime(string)
#print r

p.mysql_init()

import time
print time.time()
print time.localtime(time.time())
print time.strftime('%Y.%m.%d', time.localtime(time.time()))
r = time.strftime('%Y%m%d', time.localtime(time.time()))
print r
