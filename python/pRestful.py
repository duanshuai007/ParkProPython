#!/usr/bin/python
# -*- coding: gbk -*-

import socket
import subprocess

import json
import requests
from urlparse import urljoin
import chardet

BASE_URL = 'http://192.168.200.14:8383'
IP_PORT = ('127.0.0.1', 9876)

def get_all_user():
    rsp = requests.get(urljoin(BASE_URL, '/todos'), headers={'Content-Type': 'application/json'})
    return rsp.json()

def get_user():
    rsp = requests.get(urljoin(BASE_URL, '/todos/todo2'), headers={'Content-Type': 'application/json'})
    jsondata = rsp.json()
    string = json.dumps(jsondata)
    tup = ('hello','world')
    return rsp.json() 

#print(get_all_user().json())

#新增内容
def post_user(msg_tuple):
    #print 'Ready POST'
    rsp = ''
    try:
        length = len(msg_tuple)
        json_data = dict(task='%s:%s,%s,%s' % (msg_tuple[0],msg_tuple[1],msg_tuple[2],msg_tuple[3]))
        #print json_data
        rsp = requests.post(urljoin(BASE_URL, '/todos'), headers={'Content-Type': 'application/json'},
                data=json.dumps(json_data))
    except Exception as e:
        print 'post except'
        print e.args
    finally:
        if rsp:
            return rsp.json()
        else:
            return 'restful:close'

#print(post_user().json())

#更新内容
def put_user():
    json_data = dict(task='jojo\'s advance')
    rsp = requests.put(urljoin(BASE_URL, '/todos/todo2'), headers={'Content-Type': 'application/json'},
            data=json.dumps(json_data))
    return rsp.json()

#print(put_user().json())

#删除内容
def del_user():
    rsp = requests.delete(urljoin(BASE_URL, '/todos/todo2'), headers={'Content-Type': 'application/json'})
    return rsp.json()

def get_count():
    tup = (10,)
    return tup

#del_user()

#MESSAGE = 'Message'
#MSG_CMD_CHARGE = 'Charge'
#MSG_CMD_OTHER = 'Other'
#
#def do_socketmsg_process(string):
#    strlist = string.split(':')
#    if strlist[0] == MESSAGE :
#        if strlist[1] == MSG_CMD_CHARGE :
#            print "do something"
#        else if strlist[1] == MSG_CMD_OTHER :
#            print strlist[1]
#    else :
#        print "Message Protocol error"
#
##建立网络服务器，接收c程序发送的通信数据
#s = socket.socket()
#s.bind(IP_PORT)
#s.listen(5);
#
#while True:
#    conn,addr = s.accept()
#    while True:
#        try:
#            recv_data = conn.recv(1024)
#            if len(recv_data) == 0:
#                break;
#            print(recv_data)
#            do_socketmsg_process(recv_data)
#
#        except Exception:
#            break
#    conn.close()
##python end
