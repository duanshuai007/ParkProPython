#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime

BillingList = [5, 30, 5, 600]

#����ͣ��ʱ�������ͣ��ʱ�����Ӧ��ȡ��ͣ����
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
#�����ݿ��ж�ȡ�����ĸ�ʽ�����ַ�������Ҫ��ת��Ϊ�ַ�����ʽ
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
        #��ʾ����û�н���
        if parktime < 5:
            print '���ʱ�䣬����'
        else:
            print '��Ҫ����'
            print 'parktime=%d' % parktime
            ret = ((parktime / 30) + 1) * 5
    else:
        if parktime < (canparktime + 15):
            print '�ѽ��ѣ���������'
        else:
            print '�ɷѲ��㣬��Ҫ����ͣ����'
            ret = (((parktime - canparktime) / 30) + 1) * 5

    print 'return %d' % ret
    return ret
