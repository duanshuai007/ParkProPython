#!/usr/bin/env python
#-*- coding:utf-8 -*-

import Queue
import time
import threading

gFlag = False

def start_recv_process(arg):
    msgRecvQ = arg
    global gFlag
    while True:
#print 'in slave thread'
#       time.sleep(0.01)
        while not msgRecvQ.empty():
            print msgRecvQ.get()
            msgRecvQ.task_done()
            gFlag = True
            
def start_send_process(arg):
    msgSendQ = arg
    global gFlag
    while True:
        if gFlag == True:
            msgSendQ.put("child:send message")
            gFlag = False

def slave_thread_start(recvq, sendq):
    t0 = threading.Thread(target=start_recv_process, args=(recvq,))
    t0.setDaemon(True)   #设置为后台进程
    t0.start()
    
    t1 = threading.Thread(target=start_send_process, args=(sendq,))
    t1.setDaemon(True)   #设置为后台进程
    t1.start()

    t = [t0, t1]
    
    return t
