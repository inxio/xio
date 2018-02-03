#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from xio.core.lib.request import Request,Response
from xio.core.lib.utils import is_string, urlparse

import os
import sys
import traceback
import collections
import hashlib
import base64
import uuid
import yaml
import copy
import json
import requests
from pprint import pprint


import mimetypes
mimetypes.init()


__SCHEMES__ = {}

__XRN__ = {}

def get(scheme):
    return __SCHEMES__.get(scheme)

def bindScheme(*args,**kwargs):
    if len(args)>1:
        scheme = args[0]
        handler = args[1]
        __SCHEMES__[scheme] = handler        
    else:
        def _wrapper(handler):
            scheme = args[0]
            __SCHEMES__[scheme] = handler       
        return _wrapper

def bindNetwork(*args,**kwargs):
    if len(args)>1:
        name = args[0]
        handler = args[1]
        __XRN__[name] = handler        
    else:
        def _wrapper(handler):
            name = args[0]
            __XRN__[name] = handler       
        return _wrapper


def XrnHandler(xrn):
    nfo = xrn.split(':')
    nfo.pop(0)  # xrn
    name = nfo.pop(0)  # name
    handler = __XRN__.get(name)
    uri = ':'.join(nfo)
    return handler(uri)


class PeerHandler:

    def __init__(self,id):
        import xio
        self.id = id
        self.network = xio.context.network
        

    def __call__(self,req):
        req.path = self.id+'/'+req.path if req.path else self.id
        return self.network.request(req)


    
class pythonResourceHandler:

    def __init__(self,handler,context=None):
        from . import resource
        assert isinstance(handler,resource.Resource) 
        self.handler = handler
        self.context = context or {}
        self.debug = True
        self.client = self.context.get('client')

    def __call__(self,req):
        from . import resource

        from .app.app import App

        if isinstance(self.handler,App):
            req.path = 'www/'+req.path if req.path else 'www'

        req.context['skipjsonencode'] = True
        res = self.handler.request(req)

        req.response.status = res.status
        req.response.headers = res.headers
        return res.content
        


class pythonCallableHandler:

    def __init__(self,handler):
        self.handler = handler

    def __call__(self,req):
        return self.handler( req )      
        

class HttpHandler:

    def __init__(self,endpoint):
        self.endpoint = endpoint[:-1] if endpoint[-1]=='/' else endpoint

    def __call__(self,req):

        method = req.method
        path = req.path or '/'
        query = req.query
        headers = req.headers
        data = req.data

        path = '/'+path if path[0]!='/' else path

        method = method.lower()

        url = self.endpoint+path      

        params = query or {}

        if data and isinstance(data,list) or isinstance(data,dict):
            headers['Content-Type'] = 'application/json'
            data=json.dumps(data)

        #print(('http request ....', method, url,params,data,headers))

        h = getattr(requests,method,None)

        # fix headers (convert du _)
        headers = dict( ( key.replace('_','-'), value) for (key, value) in list(headers.items()))

        timeout = 300  # tofix => context params
        verify = True  # tofix => context params

        # fix for: Unexpected Content-Length
        if method=='head':
            data = None
           
        r = h(url,params=params,data=data,headers=headers,timeout=timeout,verify=verify)     
        status = r.status_code
        content = r.content if not r.encoding else r.text

        #print 'http response ....', status, r.headers, type(r.text)

        req.response.status = status
        req.response.headers = r.headers

        content_type = req.response.headers.get('Content-Type')
        if content_type=='application/json' and is_string(content):
            content = json.loads(content)
        
        return content
        





    

class DirectoryHandler:

    def __init__(self,directory):
        self.directory = directory
        assert os.path.isdir(directory)

    def __call__(self,req):

        path_info = req.context.get('PATH_INFO')
        if not req.path and path_info and path_info[-1]!='/':
            req.response.status = 301 
            req.response.headers['Location'] = path_info+'/'
            return None

        def _indexfile(dirpath):
            indexpath = dirpath+'/index.html'
            if os.path.isfile(indexpath):
                return indexpath

        if req.GET:

            if not req.path:
                indexpath = _indexfile(self.directory)
                return FileHandler(indexpath)(req) if indexpath else os.listdir(self.directory)

            path = self.directory+'/'+req.path if req.path else self.directory
            if os.path.isfile(path):        
                h = FileHandler(path)
                return h(req)
            elif os.path.isdir(path):
                indexpath = _indexfile(path)
                return FileHandler(indexpath)(req) if indexpath else os.listdir(path)





class FileHandler:

    def __init__(self,filepath):
        self.filepath = filepath
        assert os.path.isfile(filepath)
        self._content_type, self._content_encoding = mimetypes.guess_type(filepath)

    def __call__(self,req):

        fp = open(self.filepath, 'rb')
        req.response.headers['Content-Type'] = self._content_type
        if self._content_encoding:    
            request.response.headers['Content-Encoding'] = self._content_encoding    
        return fp

def FsHandler(filepath):

    if filepath.startswith('file://'):
        filepath = filepath[7:]

    if os.path.isdir(filepath):
        return DirectoryHandler(filepath)
    elif os.path.isfile(filepath):
        return FileHandler(filepath)

"""
to fix
"""


class IpcHandler:
    """
    not ready yet !
    """

    def __init__(self,endpoint):

        try:
            # https://pypi.python.org/pypi/requests-unixsocket/
            import requests_unixsocket
        except:
            print('WARNING requests_unixsocket not found : pip install requests_unixsocket')

        #'http+unix://%2Ftmp%2Fuwsgi_node_http2.sock/.check'

        endpoint = endpoint.replace('ipc://','').replace('/','%2F')

        self.endpoint = 'http+unix://'+endpoint
        self.unixrequests = requests_unixsocket.Session()

    def request(self,method,path,query=None,headers=None,data=None,**kwargs):

        method = method.lower()
        url = self.endpoint+path
        params = query or {}

        if data and isinstance(data,list) or isinstance(data,dict):
            headers['Content-Type'] = 'application/json'
            data=json.dumps(data)

        h = getattr(self.unixrequests,method,None)
        r = h(url,params=params,data=data,headers=headers,timeout=3)
        status = r.status_code

        return {
            'status': status,
            'headers': r.headers,
            'content': r.text,
        }
        

class WebsocketHandler:

    def __init__(self,endpoint,app=None):

        try:
            from ws4py.client.threadedclient import WebSocketClient
        except:
            print('WARNING ws4py not found : pip install ws4py')

        self._awaiting_requests = {}
        self._feedbacks = {}
        self.app = app
        self.endpoint = endpoint
        self.ws = WebSocketClient(self.endpoint, protocols=['xio'])
        self.ws.received_message = self.onreceive
        self.connected = False
        
    def __call__(self,req):
        return self.request(req.method,req.path,headers=req.headers,query=req.query,data=req.data)

    def connect(self):
        self.ws.connect()
        self.connected = True
        #self.ws.run_forever()
   

    def respond(self,method,path,query=None,headers=None,data=None,feedback=None,**kwargs):
        pass # to be overwrited        

    def request(self,method,path,query=None,headers=None,data=None,feedback=None,**kwargs):
        if not self.connected:
            self.connect()

        message = {
            'method':   method,
            'path':     path or '',
            'query':    query or {},
            'data':    data or '',
            'headers':   headers or {}
        }
        resp = self.send(message,feedback=feedback)
        return {
            'status':   resp.get('status',200),
            'headers':  resp.get('headers',{}),
            'content':  resp.get('content',''),
        }

        

    def send(self,msg,feedback=None):

        if not isinstance(msg,dict):
            self.ws.send( msg )
        else:

            # mode request/response

            id = str( uuid.uuid1() )
            msg['type'] = 'request' 
            msg['id'] = id
            self._awaiting_requests[id] = None
            if feedback:
                self._feedbacks[id] = feedback
     
            msg = json.dumps(msg)
            self.ws.send( msg )
            timeout = 5
            t0 = time.time()
            while self._awaiting_requests.get(id)==None:
                t1 = time.time()
                s = int(t1-t0)   
                if s>4: 
                    print('ws WARNING ... waiting ... since', int(t1-t0)) 
                if s>timeout:
                    return {
                        'status': 408,
                        'content': '',
                        'headers': {}
                    }
                time.sleep(0.1)
                
            info = self._awaiting_requests.pop(id) 
            return info

    def onreceive(self,msg):
        try:
            msg = json.loads(str(msg))
        except:
            msg = {}    
        type = msg.get('type')
        id = msg.get('id')
        if type=='response':
            if id in self._awaiting_requests:
                self._awaiting_requests[id] = msg
        elif type=='fragment':
            feedback = self._feedbacks.get(id)
            if feedback:
                feedback(msg['content'])
        elif type=='request':
            method = msg['method']
            path = msg['path']
            data = msg.get('data')
            query = msg.get('query')
            headers = msg.get('headers')

            try:
                assert self.app!=None, Exception('ws client could not respond to request !!! NO APP DEFINED ! ')
                response = self.app.request(method,path,headers=headers,query=query,data=data,skipjsonencode=True) 
                msg = {
                    'id': id,
                    'type': 'response',
                    'status': response.status,
                    'headers': response.headers,
                    'content': response.content
                }
            except Exception as err:
                traceback.print_exc()
                msg = {
                    'id': id,
                    'type': 'response',
                    'status': 500,
                    'content': err
                }
            self.ws.send( json.dumps(msg,default=str) )
        


bindScheme('xrn',XrnHandler)
bindScheme('file',FsHandler)
bindScheme('http',HttpHandler)
bindScheme('https',HttpHandler)
#bindScheme('ws',WebsocketHandler)
#bindScheme('wss',WebsocketHandler)
#bindScheme('ipc',IpcHandler)





