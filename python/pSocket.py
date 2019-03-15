#!/usr/bin/env python
#-*- coding:gbk -*-

import pRestful as restful
import pMysql as mysql
import socket
import select
#import chardet
import Queue
import logging
import pBilling
import pWebSocket
import threading
import time

IP_PORT = ("127.0.0.1", 9876)
BillingList = [15, 30, 5, 600]  #免费时长,计费周期,每个计费周期的价格，最大计时时间/每天最多收费值
MAX_WAIT_TIME = 1

def park_message_process(string_gbk):
    #print string_gbk
    strlist = string_gbk.split(',')
    msghead = strlist[0]
    msgtype = strlist[1]

    ret_list = [msgtype,]
    if msghead == 'Message':
        if msgtype == 'In':
            msgcolor = strlist[2]
            msgplate = strlist[3]
            msgtime = strlist[4]
            message_list = [msgcolor, msgplate, msgtime]
            r = mysql.mysql_updatedb_when_carin(message_list)
            ret_list.append(r)
        elif msgtype == 'Out':
            msgcolor = strlist[2]
            msgplate = strlist[3]
            msgtime = strlist[4]
            message_list = [msgcolor, msgplate, msgtime]
            #r = mysql.mysql_updatedb_when_carout(message_list)
            #获取停车时长
            r = False
            #检查表并更新表内的停车信息,返回车辆的驶入驶出时间长度
            r_list = mysql.mysql_getparktime_when_carout(message_list)
            if r_list :
                intime = r_list[0]
                outtime = r_list[1]
                canparktime = r_list[2]
                bill = pBilling.do_calculator(r_list)
                if bill == 0:
                    r = True
                    #车辆不欠费，允许离开。程序控制抬杆，写入数据库，
                    msg_list = [msgcolor, msgplate, intime, outtime]
                    mysql.mysql_update_leaveflag(msg_list)
                else:
                    print '请交费%d元' % bill
            ret_list.append(r)
        elif msgtype == 'OutOK' or msgtype == 'InOK':
            msgtime = strlist[2]
            message_list = [msgtype, msgtime]
            mysql.mysql_update_okflag(message_list)
            ret_list.append(False) #不需要再执行开门动作
        else:
            print 'other type'
    else:
        print 'not find Message'
    return ret_list

#仅仅将需要发送的消息放入消息队列中
#不能够判断发送是否成功
def do_set_data_to_websocket(msglist, queue):
    while msglist:
        try:
            msg = msglist.pop(0)
            queue.put(msg)
        except Exception as e:
            print e.args

#所有对mysql的操作都放在这个进程中执行，确保数据库操作的原子性
def mysql_write_process(recvq, sendq):
    timedelay = 0
    while True:
        #从消息队列中提取消息，消息有两个来源
        #1是来自websocket发送回来的上传成功确认
        #2是来自C程序的车辆驶入信息   
        while not recvq.empty():
            recvdata = recvq.get()
            length = len(recvdata)
            #print 'list len=%d' % length
            if length == 4:
                #接收到结构体 1驶入驶出消息 2消息队列 3描述符
                msg = recvdata[0]
                squeue = recvdata[1]
                outdesc = recvdata[2]
                readno = recvdata[3]
            else:
                msg = recvdata

            item = msg.split(',')
            if item[0] == 'Response':   #服务器返回的上传成功信息
                string = '%s,%s,%s,%s,%s' % (item[1], item[2],item[3],item[4],item[5])
                mysql.mysql_update_uploadflag(string)
            elif item[0] == 'Message':  #相机发送来的车辆进入信息
                result = park_message_process(msg)
                cardir = result[0]
                opendoor = result[1]
                msg_head = 'Message'
                msg_camera = '' 
                msg_cmd = ''
                if cardir == 'Out':
                    msg_camera = 'Camera02'
                    if opendoor == True:
                        msg_cmd = 'OpenDoor'
                elif cardir == 'In':
                    msg_camera = 'Camera01'
                    if opendoor == True:
                        msg_cmd = 'OpenDoor'
                if msg_camera and msg_cmd:
                    msg = '%s:%s:%s' % (msg_head, msg_cmd, msg_camera)
                    squeue.put(msg) #向队列中添加消息
                    outdesc.append(readno)   #使借口可写
            elif item[0] == 'Action': #服务器发送过来的控制命令
                if item[1] == 'Charge':  #交费信息，更新数据内的u32CanParkTime信息
                #{
                #   "Action":"Charge",
                #   "Color":"蓝",
                #   "Plate":"辽A12345",
                #   "ChargeTime":120,
                #}
                    string = '%s,%s,%s' % (item[2],item[3],item[4])
                    ret = mysql.mysql_update_canparktime(string)
                    if ret == True:
                        print 'update canparktime success'
        time.sleep(0.1)
        timedelay = timedelay + 1
        if timedelay > (10 * 5) :
            timedelay = 0
            itemlist = mysql.mysql_get_noupload_item()
            do_set_data_to_websocket(itemlist, sendq)
            itemlist = mysql.mysql_get_complete_item()
            if itemlist:
                stringlist = mysql.mysql_insert_item_into_histroytb(itemlist)
                mysql.mysql_remove_item_in_curtb(stringlist)

def SocketInit():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ipport = ('127.0.0.1', 9876)
    server.bind(ipport)
    server.listen(5)
    return server

def main_process():
    sendQueue = 0
    resvQueue = 0
    server = SocketInit()
    inputs = [server,]
    outputs = []
    message_queue = {}
    
    results = pWebSocket.run()
    if results:
        sendQueue = results[0]
        resvQueue = results[1]
    else:
        print 'websocket.py has error'
        return

    p = threading.Thread(target = mysql_write_process, args = [resvQueue, sendQueue])
    p.setDaemon(True)
    p.start()

    while True :
        readable,writeable,exceptional = select.select(inputs, outputs, inputs, 0)
        if not (readable or writeable or exceptional):
            continue
        for r in readable:
            #读取从C程序发来过来的车辆进出的信息
            if r is server:
                conn,addr = server.accept()
                print 'new connect'
                conn.setblocking(False)
                inputs.append(conn)
                message_queue[conn] = Queue.Queue()
            else:
                try:
                    recv_data = r.recv(1024)
                    #print 'recv %s' % recv_data
                except:
                    err_msg = "Client Error!"
                    logging.error(err_msg)
                else:
                    if recv_data:
                        #接收到c程序发来的消息，进行处理
                        print 'recv from camera:%s' % recv_data
                        msg_list = (recv_data, message_queue[r], outputs, r)
                        resvQueue.put(msg_list)
                    else:
                        print 'Client Close!'
                        inputs.remove(conn)
                        del message_queue[r]
                    
        for w in writeable:
            #发送给C程序控制抬杆落杆的消息
            try:
                next_msg = message_queue[w].get_nowait()   #非阻塞获取
            except Queue.Empty:
                err_msg = 'Output Queue is Empty'
                logging.error(err_msg)
                outputs.remove(w)
            except Exception, e:
                err_msg = 'Send Data Error!ErrMsg:%s' % str(e)
                logging.error(err_msg)
                if w in outputs:
                    outputs.remove(w)
            else:
                try:
                    print 'socket send %s' % next_msg
                    w.send(next_msg)
                    outputs.remove(w)
                except Exception, e:
                    err_msg = "Send Data Error! ErrMsg:%s" % str(e)
                    logging.error(err_msg)

        for e in exceptional:
            print 'socket exceptional'
            if e in outputs:
                outputs.remove(e)
            inputs.remove(e)

    conn.close()
    server.close()

if "__main__" == __name__:
    main_process()

