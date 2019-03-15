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

def on_message(ws, message):
    print 'recv:%s'% message

def on_error(ws, error):
    print 'error:%s' % error

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        #for i in range(3):
        for i in range(3):
            ws.send("Hello Tree 3 !")
            time.sleep(1)
#        i=0
#        while True:
#            time.sleep(1)
#            ws.send("Hello %d" % i)
#            i=i+1
#        time.sleep(1)
#        ws.close()
#        print("thread terminating...")
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://192.168.200.202:8080/echo",
            on_message = on_message,
            on_error = on_error,
            on_close = on_close)
    ws.on_open = on_open
    ws.run_forever(ping_interval=60,ping_timeout=5)
