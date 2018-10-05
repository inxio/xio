#!/usr/bin/env python
#-*- coding: utf-8 -*--

import xio

import os
import sys
from os import sys, path
sys.path.insert(0, path.dirname(path.abspath(__file__)))


app = xio.app(__name__)


app.bind('www/test', lambda req: 'ok')
#app.bind('www/root', lambda req: app.request(req))
#app.bind('www/root', app)


@app.bind('www/root')
def _(req):
    print('??????????')
    server = req.context.get('xio.wsgi.app')
    resp = server.request(req)
    print('====', resp)
    return resp


@app.bind('www/debug')
def _(req):
    return req._debug()

if __name__ == '__main__':

    app.main()
