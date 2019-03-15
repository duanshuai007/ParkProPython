#!/usr/bin/python
#-*- coding:utf-8 -*-

import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import Queue
import threading
import time
import json
import random
import ssl

#接收主程序发送过来的上传信息
gRecvList = []
#发送上传成功信息给主程序
gSendList = []
gAlreadySendList = []

seq = ['Color','Plate','Dir', 'InTime','OutTime','Identify']
gMyDict = dict.fromkeys(seq)

gConnectIsClosed = False
#创建一个发送的链表
#链表内容包括发送的内容，信息的id，发送使能标志，

#接收数据处理函数
def on_message(ws, message):
    global gSendList 
    global gAlreadySendList
    print 'websocket thread recv: %s'% message
    pos = 0
    msg_dict = json.loads(message)
    if msg_dict:
#if msg_dict.has_key('Response'):
        identify = msg_dict['Identify']
        while pos < len(gAlreadySendList):
            item_dict = gAlreadySendList[pos]
            if item_dict:
                identify_1 = item_dict['Identify']
                if identify == identify_1:
                    string = 'Response,%s,%s,%s,%s,%s' \
                                    % (item_dict['Dir'], item_dict['Color'], item_dict['Plate'], item_dict['InTime'], item_dict['OutTime'])
                    gSendList.append(string)
                    del gAlreadySendList[pos]
            pos = pos + 1
#        elif msg_dict.has_key('Action'):
#            string = 'Action,%s,%s,%s,%d' % (msg_dict['Action'], msg_dict['Color'], msg_dict['Plate'], msg_dict['ChargeTime'])
#            gSendList(string)

def on_error(ws, error):
    global gSendList
    print '#### error:%s ####' % error
    gSendList.append("WebSocket:Error")

def on_close(ws):
    global gSendList
    global gConnectIsClosed
    print("### closed ###")
    gSendList.append("WebSocket:Close")
    gConnectIsClosed = True

#发送处理函数
def on_open_run(ws):
    global gRecvList
    global gSendList
    global gAlreadySendList
    global gConnectIsClosed
    while True:
        try:
            while gRecvList:
                #从接收列表中取出一条信息发送给websocket服务器
                msg_dict = gRecvList.pop(0)
                #将该条信息加入到已发送的消息列表
                gAlreadySendList.append(msg_dict)
                #print 'msg_dict:%s' % msg_dict
                msg_json = json.dumps(msg_dict, ensure_ascii=False, indent=4)
                #发送消息
                print 'websocket thread send: %s' % msg_json
                ws.send(msg_json)
            #重连：如果检测到标志置位，则推出该线程。否则再重连后会出现两个该线程
            #从而出现错误
            if gConnectIsClosed == True:
                gConnectIsClosed = False
                print 'connect closed'
                break
        except Exception as e:
            print '[except] on_open_run'
            print e.args
            gSendList.append("WebSocket:Error")
                

#打开即发送处理函数
def on_open(ws):
    print 'on open'
    t = threading.Thread(target=on_open_run, args=[ws,])
    t.setDaemon(True)
    t.start()
#另一种创建线程的方式
#thread.start_new_thread(on_open_run, (1,))

def mainProcess():
    #重连：标志需要设置为全局标志
    global gConnectIsClosed
    gConnectIsClosed = False
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("ws://192.168.200.14:8080/echo",
            on_message = on_message,
            on_error = on_error,
            on_close = on_close)
    ws.on_open = on_open
    ws.run_forever(ping_interval=60,ping_timeout=5,sslopt={"cert_reqs": ssl.CERT_NONE})
    print 'mainProcess end'
    ws.close()
    
#与主程序之间数据交互
#1.从消息队列中接收主程序发送过来的数据
#2.从list中依次取出需要发送给主程序的数据
def dataProcess(sq, rq, pthread):
    global gRecvList
    global gSendList
    global gMyDict
    while True:
        #接收数据
        #.1
        while not rq.empty():
            try:
                msg = rq.get()
                item = msg.split(',')
                gMyDict.clear()
                gMyDict['Dir']      = item[0]
                gMyDict['Color']    = item[1]
                gMyDict['Plate']    = item[2]
                gMyDict['InTime']   = item[3]
                gMyDict['OutTime']  = item[4]
                gMyDict['Identify'] = random.randint(1, 1000)
                #寻找字典list中是否有相近记录，如果有则替换掉
                pos = 0
                while pos < len(gAlreadySendList):
                    item_dict = gAlreadySendList[pos]
                    if item_dict:
                        if gMyDict['Color'] == item_dict['Color'] and gMyDict['Plate'] == item_dict['Plate'] and \
                            gMyDict['Dir'] == item_dict['Dir'] and gMyDict['InTime'] == item_dict['InTime'] and \
                            gMyDict['OutTime'] == item_dict['OutTime']:
                            #gRecvList['Identify'] = item_dict['Dir']
                            break
                    pos = pos + 1
                if pos == len(gAlreadySendList):   #没找到同样的车辆信息
                    gRecvList.append(gMyDict)
            except Exception as e:
                print e.args
        #发送数据
        #.2
        while gSendList:
            try:
                msg = gSendList.pop(0)
                sq.put(msg)
            except Exception as e:
                print e.args
        #重连：如果断开链接mainProcess线程就会退出变为非alive状态
        #所以需要重新建立mainprocess线程
        if not pthread.isAlive():
            print 'websocket thread end with error'
            #websocket 客户端进程
            webthread = threading.Thread(target = mainProcess, args = [])
            webthread.setDaemon(True)
            webthread.start()
            pthread = webthread
            time.sleep(1)


def run():
    rQueue = Queue.Queue(64)
    sQueue = Queue.Queue(64)
    #websocket 客户端进程
    myThread = threading.Thread(target = mainProcess, args = [])
    myThread.setDaemon(True)
    myThread.start()
    #与主程序之间的数据交换线程
    dataThread = threading.Thread(target = dataProcess, args = [sQueue, rQueue, myThread])
    dataThread.setDaemon(True)
    dataThread.start()

    result_tup = (rQueue, sQueue)
    return result_tup

#end
