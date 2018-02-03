#!/usr/bin/env python
#-*- coding: utf-8 -*--

import xio

app = xio.app(__name__)

app.put('www/test1', lambda req: 'ok test1')

@app.bind('www/test2')
def _(req): 
    return 'ok test2'

if __name__ == '__main__':

    app.main()

