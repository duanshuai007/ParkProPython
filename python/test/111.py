#!/usr/bin/env python 
#-*- coding:utf-8 -*-

from bottle import route, run

@route('/hello/:name') 
def index(name='World'):
    return '<b>Hello %s!</b>' % name 
    
run(host='0.0.0.0', port=8080)
