#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import posixpath
import sys
import traceback
import time

import collections

import requests
import json

import base64
import uuid

from pprint import pprint

import xio



from xio.core.env import getDefaultEnv, setDefaultEnv

if __name__ == '__main__':


    p = sys.argv[1:]+[None]*5
    action = p.pop(0) if p else None
    param1 = p.pop(0) if p else None
    param2 = p.pop(0) if p else None
    param3 = p.pop(0) if p else None

    """
    # redirect to docker commands
    if action=='node':
        if param1 in 'build test run console stop logs'.split(' '):
            import os
            params = ' '.join(sys.argv[2:])
            os.system('cd /apps/xio/docker && ./xio.sh '+params)
        sys.exit()
    """


    data = getDefaultEnv()


    endpoint = data.get('network')
    id = data.get('id')
    token = data.get('token')

    print ('\n\n===================',' '.join(sys.argv),'\n')
    print ('\t id', data.get('id'))
    print ('\t network', endpoint)
    print ()

    if action=='init':

        seed = raw_input('seed (leave blank for automatic generation): ')
        password = raw_input('password : ') or ''
        network = raw_input('network : ') or ''
        
        user = xio.user(seed=seed)

        data = dict()
        data['id'] = user.id
        data['token'] = user.token
        data['key'] = user.key.encrypt(password)
        data['network'] = 'http://127.0.0.1:8080'

        setDefaultEnv(data)
        sys.exit()

    if action=='run':
	    app = xio.app()
	    app.run(ws=8484)

    if action=='test':
        import os
        import os.path
        basedir = os.path.dirname( xio.__file__)
        os.system('cd '+basedir+' && python -m unittest discover')
        sys.exit()

    if action=='login':

        password = raw_input('password : ') or ''
        
        cryptedkey = data.get('key')
        from xio.core.common.crypto import decrypt
        key = decrypt(cryptedkey, password)
        user = xio.user(key=key)
        data['token'] = user.token
        xio.setDefaultEnv(data)
        pprint(data)
        sys.exit()

    if endpoint and action and token:

        xio.env('node', data.get('xio.node') )
        xio.env('id', data.get('xio.id') )
        xio.env('token', data.get('xio.token') )

        client = xio.app(endpoint)
        if endpoint[0]!='/':

            method = action.upper()
            path = param1 or ''
            path = '/'+path if path and path[0]!='/' else path
            resp = client.request(method,path or '')

            print ('\n>>> %s %s ' % (method,repr(param1)))
            print ('\tstatus:', resp.status)
            print ('\tcontent_type:', resp.content_type)
            print 
            if resp.content_type=='application/json':
                pprint(resp.content)
            else:
                print ('\n', resp.content)
    else:
        print ('commands : ')
        print ('\t init          : initialize account')
        print ('\t about         : retreive information about current network')
        print ('\t test          : run all xio tests')
        print ('\n')        

    print ('\n')

    









