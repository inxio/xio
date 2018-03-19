#!/usr/bin/env python
#-*- coding: utf-8 -*--

import xio

app = xio.app(__name__)

app.put('www/test1', lambda req: 'ok test1')

@app.bind('www/test2')
def _(req): 
    return 'ok test2'

@app.bind('www/testquota')
def _(req):
    req.require('quota',10)
    return 'ok %s' % req.stat


@app.bind('www/testcache')
def _(req):
    import random
    req.response.ttl = 10
    return random.random() 



if __name__ == '__main__':

    app.main()

