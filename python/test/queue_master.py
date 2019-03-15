#!/usr/bin/env python
#-*- coding:utf-8 -*-

import Queue
import time
import threading
import queue_slave
import os
import signal

#该程序向子程序发送的消息队列
msgSendQueue = Queue.Queue(32)
#该程序从子程序接收的消息队列
msgRecvQueue = Queue.Queue(32)

def func(arg):
    print arg
    q = arg
    while True:
        while not q.empty():
            print q.get()
            q.task_done()

#p = Process(target=func, args=mQueue)

t = queue_slave.slave_thread_start(msgSendQueue, msgRecvQueue)

p = threading.Thread(target=func,args=(msgRecvQueue,))
p.setDaemon(True)
p.start()

while True:
    print 'main process'
    msgSendQueue.put("what is it!")
    time.sleep(1)
    if not t[0].isAlive():
        break
    if not t[1].isAlive():
        break
    if not p.isAlive():
        break
        
print 'main end'
