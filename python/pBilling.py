#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime

BillingList = [5, 30, 5, 600]

#根据停车时间和允许停车时间计算应收取的停车费
def do_calculator(rlist):
    intime = rlist[0]
    outtime = rlist[1]
    canparktime = rlist[2]
    ret = 0
    
    string = outtime.split(' ')
    string_date = string[0]
    string_time = string[1]
    string_date_s = string_date.split('-')
    string_time_s = string_time.split(':')
    t1 = datetime.datetime(int(string_date_s[0]), int(string_date_s[1]), int(string_date_s[2]), 
        int(string_time_s[0]), int(string_time_s[1]), int(string_time_s[2]))
#从数据库中读取出来的格式不是字符串，需要先转换为字符串格式
    intime_str = '%s' % intime
    string = intime_str.split(' ')
    string_date = string[0]
    string_time = string[1]
    string_date_s = string_date.split('-')
    string_time_s = string_time.split(':')
    t2 = datetime.datetime(int(string_date_s[0]), int(string_date_s[1]), int(string_date_s[2]), 
        int(string_time_s[0]), int(string_time_s[1]), int(string_time_s[2]))
#ret = park_min
#print 't2=%s' % t2 + 't1=%s' % t1
    parktime = (t1-t2).seconds / 60 
    if canparktime == 0:
        #表示从来没有交费
        if parktime < 5:
            print '免费时间，放行'
        else:
            print '需要交费'
            print 'parktime=%d' % parktime
            ret = ((parktime / 30) + 1) * 5
    else:
        if parktime < (canparktime + 15):
            print '已交费，可以走了'
        else:
            print '缴费不足，需要补足停车费'
            ret = (((parktime - canparktime) / 30) + 1) * 5

    print 'return %d' % ret
    return ret
