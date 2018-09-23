#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import requests
import json
import base64
from pprint import pprint
from xio.core.lib.utils import sha1

import sys
if sys.version_info.major == 2:
    from Cookie import SimpleCookie
    from urllib import unquote
else:
    from http.cookies import SimpleCookie
    from urllib.parse import unquote


__ALLOWED_METHODS__ = ['HEAD', 'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'CONNECT']


def request(method, path, **kwargs):

    if '://' in path:
        import requests
        url = path
        h = getattr(requests, method.lower())
        params = kwargs.get('query') or {}
        headers = kwargs.get('headers') or {}
        data = kwargs.get('data') or None
        r = h(url, params=params, data=data, headers=headers)
        response = Response(r.status_code)
        response.content_type = r.headers['content-type']
        response.headers = r.headers
        response.content = r.json() if response.content_type == 'application/json' else r.text
        return response

    return Request(method, path, **kwargs)


class UnhandledRequest:
    """ redirect to default hander """


class Request(object):

    PASS = UnhandledRequest

    def __init__(self, method, path, query=None, headers=None, data=None, context=None, debug=False, client=None, client_context=None, server=None, **kwargs):

        context = context or {}
        headers = headers or {}

        path = path[1:] if path and path[0] == '/' else path

        xmethod = headers.get('XIO-method', headers.get('xio_method')) if headers else None
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
            setattr(self, m, False)

        # MOD DEV ONLY  ???
        if method == 'GET' and path and '.' in path:
            p = path.split('/')
            last = p.pop()
            if last and last[0] == '.':
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

        setattr(self, method.upper(), True)
        if xmethod:
            setattr(self, xmethod.upper(), True)

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

        self.cookie = Cookie(self)
        self.response = Response(200)

        self._uid = None
        self._stack = []  # debug only
        self.stat = None

        self._server = server
        self._client = client
        self._client_context = client_context

        self.init()

    def init(self):
        # used for rebuild stuff if something changed (eg token)
        # pb1: resource != app != server
        # pb2: resource and/or root seem to be added AFTER init !
        self.server = self.server or self.context.get('root', self.context.get('app', self.context.get('resource', None)))
        self.client = ReqClient(self, self._client_context, peer=self._client)

    def __repr__(self):
        return 'REQUEST %s %s' % (self.xmethod or self.method, repr(self.path))

    def _debug(self):
        return {
            'method': self.method,
            'path': self.path,
            'xmethod': self.xmethod,
            'headers': self.headers,
            'query': self.query,
            'data': self.data,
            'input': self.input,
            'profile': self.profile,
            'client': {
                'auth': {
                    'scheme': self.client.auth.scheme,
                    'token': self.client.auth.token,
                    'data': self.client.peer.key.tokendata if self.client.peer else None
                },
                'id': self.client.id,
                'context': self.client.context,
                'peer': self.client.peer,


            },
            'server': self.server,

            'context': self.context
        }

    def service(self, name):
        resource = self.context.get('root')
        pprint(self.context)
        if resource and resource.os:
            resource.debug()
            service = resource.os.get('services/%s' % name)
            print('service', name, service)
            if service.status in (200, 201):
                return service

    def require(self, key, value, content=None):

        if key == 'auth':
            print('req.require', value, '=>', self.client.auth.scheme)
            if not self.client.auth.scheme or not self.client.auth.token or not self.client.id:
                self.response.headers['WWW-Authenticate'] = '%s realm="%s", charset="UTF-8"' % (value, 'xio realm')
                raise Exception(403)
        elif key == 'signature':
            # quick testcase : if peer able to sign we convert original data
            # using virtual peer capacity ? eg: req.client.sign(tx) ... direct if _peer else http401
            # if req.client._peer:
            #    signed = c.sign(req.client._peer.key.ethereum.private)
            signature = self.headers.get('XIO-Signature')
            if not signature:
                self.response.headers['WWW-Authenticate'] = '%s realm="%s", charset="UTF-8"' % (value, 'xio realm')
                self.response.status = 402
                raise Exception(402, content)
            return signature
        elif key == 'scope':
            print('scope?')
            pprint(self.client.data)
            if not value in self.client.data.get('scope'):
                raise Exception(401, 'scope not allowed')
        elif key == 'quota':
            # get relevant service
            service = self.service('stats')
            if service:
                uid = self.uid()
                stat = service.get(uid)
                current = int(stat.content or 0)  # .get('hourly')
                print('????curent stat', current, value)
                if current >= value:
                    raise Exception(429, 'QUOTA EXCEEDED')
                service.incr(uid)
        else:
            raise Exception('unknow require rule : %s' % key)

    def uid(self):
        """
        generate uniq identifier for stats, cache, ...
        warning about 
        - userid and/or profile for cache 
        - qurey sting key orders 
        """
        if not self._uid:
            import hashlib
            import json

            struid = '%s-%s' % (self.fullpath, json.dumps(self.input, sort_keys=True))
            print(struid)

            uid = sha1(struid)
            print(uid)
            self._uid = uid
        return self._uid

    def getQuotas(self):
        """
        retreive quotas provided by node
        """
        quotas = self.headers.get('XIO-quotas') or self.headers.get('xio_quotas')
        if quotas:
            infos = json.loads(quotas)
            quotas = {}
            if infos[0]:
                quotas['ttl'] = infos[0]
            if infos[1]:
                quotas['storage'] = infos[1]
            if infos[2]:
                quotas['request'] = infos[2]
            if infos[2]:
                quotas['items'] = infos[3]
        return quotas or {}

    def __getattr__(self, name):
        return self.__dict__[name] if name in self.__dict__ else None


class Response:

    def __init__(self, status):
        self.status = status
        self.headers = {}
        self.content_type = 'text/plain'
        self.content = None
        self.ttl = 0
        self.traceback = None

    def __repr__(self):
        return 'RESPONSE %s %s' % (self.status, self.content_type)


class Cookie:

    def __init__(self, req):
        self._req = req
        self._data = req.context.get('cookies', {})

    def set(self, key, value):

        import http.cookies

        cookie = http.cookies.SimpleCookie()

        cookie[key] = str(value)
        cookie[key]["path"] = "/"
        #cookie[key]["expires"] = 3600

        strcookie = cookie.output()
        valuecookie = strcookie.replace('Set-Cookie: ', '')
        self._req.response.headers['Set-Cookie'] = valuecookie

    def get(self, key):
        value = self._data.get(key)
        return unquote(value) if value else None


class Auth:

    scheme = None
    token = None

    def __init__(self, client):
        self.req = client.req

        authorization = self.req.headers.get('Authorization', self.req.headers.get('authorization'))
        if not authorization and client.context:
            authorization = client.context.get('authorization')

        if not authorization:
            authorization = self.req.cookie.get('XIO-AUTH')

        if authorization:
            scheme, token = authorization.split(' ')
            self.scheme = scheme.lower()
            self.token = token


class ReqClient:

    def __init__(self, req, context=None, peer=None):

        import xio

        self.req = req
        self.id = None
        self.peer = None
        self._peer = peer  # warning originale peer for testcase (correct id require token based raccount ecover)
        self.context = context
        self.auth = Auth(self)
        self.data = dict()

        # if not peer we create a keyless user from token
        if self.auth.token:

            if self.auth.scheme == 'basic':
                login, password = base64.urlsafe_b64decode(self.auth.token).split(b':')
                if login == b'seed':
                    user = xio.user(seed=password)
                    self.auth.scheme = 'bearer'
                    self.auth.token = user.key.generateToken('xio/ethereum')

            self.peer = xio.user(token=self.auth.token)
            self.id = self.peer.id if self.peer else None
            self.data = self.peer.key.tokendata
            self.data.setdefault('scope', [])
            if self.id and xio.env.get('adminuser') == self.id:
                self.data['scope'].append('admin')

        self._feedback = req.context.get('feedback')
        self._wsendpoint = req.context.get('wsendpoint')
        self.send = self._send if self._feedback else None
        self.onreceive = self._onreceive if self._wsendpoint else None

        if context:
            # check authorization from context
            if 'authorization' in context:
                req.headers['Authorization'] = context.pop('authorization')
            self.context = context
            req.headers['XIO-context'] = json.dumps(self.context)
        else:
            get_context = req.query.get('xio_context', {})
            self.context = req.headers.get('XIO-context', req.headers.get('xio_context', get_context))

            if self.context and self.context[0] == '{':
                self.context = json.loads(self.context)

    def auth(self):
        return bool(self.token)

    def __bool__(self):
        return self.id != None

    def __nonzero__(self):
        return self.id != None

    def _ws_onreceive(self, msg):
        self._wsendpoint.send(msg)

    def _ws_send(self, msg):
        self._feedback(msg)
