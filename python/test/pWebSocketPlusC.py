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

class pWebSocket():
    def __init__(self):
        websocket.enableTrace(True)
        
    def on_message(ws, message):
        print 'recv:%s'% message

    def on_error(ws, error):
        print 'error:%s' % error

    def on_close(ws):
        print("### closed ###")

    def on_open(ws):
        def run(*args):
            for i in range(3):
                ws.send("Hello Tree 3 !")
                time.sleep(1)
        thread.start_new_thread(run, ()) 

    def run():
        ws = websocket.WebSocketApp("ws://192.168.200.202:8080/echo",
            on_message = on_message,
            on_error = on_error,
            on_close = on_close)
        ws.on_open = on_open

