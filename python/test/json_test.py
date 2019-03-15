#!/usr/bin/env python
#-*- coding:utf-8 -*-


import json

data = [
{
    'color':'À¶',
    'plate':'LA12345',
    'intime':'2019-02-22 14:33:22',
    'outtime':'2019-03-01 00:00:00',
}
]

seq = ['color','plate','intime','outtime']
mydict = dict.fromkeys(seq)
print mydict

json_str = json.dumps(data, ensure_ascii=False, indent=4)
print data
print json_str
#d = json.loads(json_str)
#print d
#for val in d:
#    for item in val:
#        print item

import random

print random.randint(1,1000)
