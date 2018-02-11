#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import requests
import json


__ALLOWED_METHODS__ = ['HEAD','GET','POST','PUT','DELETE','PATCH','OPTIONS','CONNECT'] 

def request(method,path,**kwargs): 

    if '://' in path:
        import requests
        url = path
        h = getattr(requests,method.lower())
        params = kwargs.get('query') or {}
        headers = kwargs.get('headers') or {}
        data = kwargs.get('data') or None
        r = h(url,params=params,data=data,headers=headers)
        response = Response(r.status_code)
        response.content_type = r.headers['content-type']
        response.headers = r.headers
        response.content = r.json() if response.content_type=='application/json' else r.text
        return response
        

    return Request(method,path,**kwargs)



class UnhandledRequest:
    """ redirect to default hander """

class Request(object): 

    PASS = UnhandledRequest

    def __init__(self,method,path,query=None,headers=None,data=None,context=None,debug=False,client=None,client_context=None,**kwargs): 
       
        context = context or {}
        headers = headers or {}

        path = path[1:] if path and path[0]=='/' else path
        
        xmethod = headers.get('XIO-method',headers.get('xio_method')) if headers else None 
        if xmethod:
            xmethod = xmethod.upper()
            method = 'POST'

        if not xmethod and not method.upper() in __ALLOWED_METHODS__:
            xmethod = method.upper()
            method = 'POST'

            if not 'XIO-method' in headers and not 'xio_method' in headers:
                headers['XIO-method'] = xmethod
        method = method.upper()

        for m in __ALLOWED_METHODS__:
            setattr(self,m,False)

        # MOD DEV ONLY  ??? 
        if method=='GET' and path and '.' in path: 
            p = path.split('/')
            last = p.pop()
            if last and last[0]=='.':     
                newmethod = last[1:].upper()
                if not newmethod in __ALLOWED_METHODS__:      
                    xmethod = newmethod
                    method = 'POST'
                else:
                    method = newmethod
                    xmethod = None
                    
                path = '/'.join(p) 
                data = query
                query = None
                headers['XIO-method'] = xmethod

        #/MOD DEV ONLY 

        setattr(self,method.upper(),True)
        if xmethod:
            setattr(self,xmethod.upper(),True)

        self.method = method
        self.xmethod = xmethod
        self.path = path
        self.fullpath = self.path
        self.context = context or {}
        self.headers = headers 
        self.debug = False

        self.query = query or {}
        self.data = data or {}
        self.input = self.data or self.query

        self.cookie = Cookie( self)
        self.response = Response(200)

        # debug
        self._stack = []

        self.log = getattr(self.context.get('root'),'log',None)
        self.server = self.context.get('root') # do not work : to fix
        
        # handling client
        if client:
            self.headers['Authorization'] = 'Bearer %s' % client.token
            client = ReqClient(self,client,client_context)
        else:
            login = password = token = None
            token = self.headers.get('XIO-token',self.headers.get('xio_token', self.context.get('cookies',{}).get('token') ))
            authorization = self.headers.get('Authorization',self.headers.get('authorization' ) ) 
            if authorization:
                scheme, data = authorization.split(None, 1)
                if scheme.lower() == 'basic':
                    import xio
                    login, password = data.decode('base64').split(':', 1)
                    user = xio.user(seed=login+password)
                    token = user.token
                    self.cookie.set('token',token)
                elif scheme.lower() == 'bearer':
                    token = data
            else:
                token = self.headers.get('XIO-token',self.headers.get('xio_token', self.context.get('cookies',{}).get('token') )) 
        
            client = ReqClient(self,token,client_context)
        
        self.client = client
        

    def __getattr__(self, name):
        return self.__dict__[name] if name in self.__dict__ else None


    def __repr__(self):
        return 'REQUEST %s %s' % (self.xmethod or self.method,repr(self.path))

    def _debug(self):
        return {
            'method': self.method,
            'path': self.path,
            'xmethod': self.xmethod,
            'headers': self.headers,
            'query': self.query,
            'data': self.data,
            'profile': self.profile,
            'client': {
                'id': self.client.id,
                'token': self.client.token,
                'context': self.client.context,
                'peer': self.client.peer
            },
            'server': self.server,
        }


class Response:

    def __init__(self,status):
        self.status = status
        self.headers = {}
        self.content_type = 'text/plain'
        self.content = None
        self.ttl = 0


    def __repr__(self):
        return 'RESPONSE %s %s' % (self.status,self.content_type)


class Cookie:

    def __init__(self,req):
        self._req = req
        self._data = req.context.get('cookies',{}) 

    def set(self,key,value):

        import http.cookies

        cookie = http.cookies.SimpleCookie(  )

        cookie[key] = str(value)
        cookie[key]["path"] = "/"
        #cookie[key]["expires"] = 3600
            
        strcookie = cookie.output()
        valuecookie = strcookie.replace('Set-Cookie: ','')
        self._req.response.headers['Set-Cookie'] = valuecookie

    def get(self,key):
        return self._data.get(key)


class ReqClient:

    def __init__(self,req,token,context=None):
        self.req = req
        self.id = None
        self.peer = None
        if hasattr(token,'id'):
            peer = token
            self.id = peer.id
            self.token = peer.token
            self.peer = peer
        else:    
            self.token = token
            if token:
                import xio
                account = xio.user(token=token)
                self.id = account.id    

        self._feedback = req.context.get('feedback')
        self._wsendpoint = req.context.get('wsendpoint')
        self.send = self._send if self._feedback else None
        self.onreceive = self._onreceive if self._wsendpoint else None

        if context:
            self.context = context
            req.headers['XIO-context'] = json.dumps(self.context)    
        else:    
            get_context = req.query.get('xio_context',{})
            self.context = req.headers.get('XIO-context',req.headers.get('xio_context',get_context))
    
            if self.context and self.context[0]=='{':
                self.context = json.loads(self.context)

    def auth(self):
        return bool(self.token)

    def __bool__(self):
        return self.id!=None 

    def __nonzero__(self):
        return self.id!=None 

    def _ws_onreceive(self,msg):
        self._wsendpoint.send(msg)

    def _ws_send(self,msg):
        self._feedback(msg)





