#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import absolute_import

import threading
import time
from pprint import pprint
import traceback
import json
import sys


from cgi import parse_qs, escape

if sys.version_info.major == 2:
    from cgi import parse_qs, escape
    import httplib
    import urllib
    from urllib import unquote_plus
    from httplib import responses as http_responses
    from Cookie import SimpleCookie

    def _send(content):
        return content
else:
    from http.client import responses as http_responses
    import http.client
    from http.cookies import SimpleCookie
    import urllib.error
    from urllib.parse import unquote_plus
    from xio.core.lib.utils import to_bytes

    def _send(content):
        return to_bytes(content)


def is_string(s):
    try:
        return isinstance(s, basestring)
    except NameError:
        return isinstance(s, str)


class Httpd(threading.Thread):

    def __init__(self, h, port):
        threading.Thread.__init__(self)
        self.daemon = True
        self.h = h
        self.port = port
        self.target = self.run

    def start(self):
        threading.Thread.start(self)

    def run(self):

        from gevent.pywsgi import WSGIServer

        self.httpd = WSGIServer(('', self.port), self.h)
        self.httpd.start()

        self.port = self.h.port = self.httpd.get_environ().get('SERVER_PORT')
        print('httpd running ... port=', self.port)
        self.httpd.serve_forever()

    def stop(self):
        self.httpd.shutdown()


class HttpService:

    def __init__(self, app=None, path='', endpoint=None, port=8080, context=None):
        self.app = app
        self.path = path
        assert self.app != None
        self.endpoint = endpoint
        self.port = port
        self.context = context
        self.httpd = Httpd(self, port)

    def start(self):
        self.httpd.start()

    def stop(self):
        self.httpd.stop()

    def __call__(self, environ, start_response=None):
        #print('---- http.__call__',environ)
        if not environ or not callable(environ.get):  # fix bug /run/services
            return
        try:
            environ['xio.wsgi.app'] = self.app
            method = environ.get('REQUEST_METHOD', 'GET')
            path = environ.get('PATH_INFO', '/')
            if path[0] != '/':
                path = '/404'

            query = {}
            for k, v in list(parse_qs(environ.get('QUERY_STRING', '')).items()):
                query[k] = v[0] if len(v) == 1 else v

            headers = {}
            for k, v in list(environ.items()):
                # warning headers with _ are filtered by wsgi !
                # we re unable to rtreive the original name
                if k.startswith('HTTP_'):
                    headers[k[5:].lower()] = v
                elif k == 'CONTENT_TYPE':
                    # fix content_type
                    headers[k.lower()] = v

            post_params = {}
            post_data = None

            if method in ('PUT', 'POST', 'PATCH'):

                import cgi

                # bug with cgi and content-length : https://bugs.python.org/issue27777
                # todo - handle binary (need to use CONTENT_LENGTH)

                if headers.get('content_type') == 'application/json':
                    import json
                    post_input = environ['wsgi.input'].read()
                    print('----------', post_input)
                    post_data = json.loads(post_input)
                else:
                    # warning too many bugs on cgi
                    fs = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)

                    if not fs.list:
                        post_input = fs.value
                        if headers.get('content_type') == 'application/json':
                            import json
                            print('----------', post_input)
                            post_data = json.loads(post_input)
                    else:
                        for key in fs:
                            val = fs[key]
                            if val.filename:
                                import tempfile
                                tmpfile = tempfile.TemporaryFile('w')
                                tmpfile.write(val.file.read())
                                post_params[key] = (tmpfile, val.filename)
                            else:
                                post_params[key] = unquote_plus(val.value)

                        post_data = post_params

            context = environ

            # cookies handling
            cookies = {}
            cookie_string = environ.get('HTTP_COOKIE')
            if cookie_string:
                c = SimpleCookie()
                c.load(cookie_string)
                for k, v in list(c.items()):
                    cookies[k] = v.value
            context['cookies'] = cookies
            context['cookies_debug'] = environ.get('HTTP_COOKIE')

            # set context

            pathinfo = environ.get('PATH_INFO')

            path = self.path + path if self.path else path
            #path = 'www'+path if path else 'www'

            import xio

            request = xio.request(method, path, headers=headers, query=query, data=post_data, context=context, server=self.app)

            response = self.app.render(request)

            assert response.status

            import inspect
            import json
            if isinstance(response.content, dict) or isinstance(response.content, list) or inspect.isgenerator(response.content):
                if inspect.isgenerator(response.content):
                    response.content = [r for r in response.content]
                response.content_type = 'application/json'
                response.content = json.dumps(response.content, indent=4, default=str)

            #print('HTTP RESPONSE', response.content)

            # if request.OPTIONS:
            # add header Access-Control-Allow-Origin => to fix
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS, POST, PUT, PATCH, DELETE, CONNECT'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Content-Length, Date, Accept, Authorization, XIO-method, XIO-context'

            import inspect

            """ 403 mean forbiden so confusion 
            if response.status == 403:
                response.headers['WWW-Authenticate'] = 'Basic realm="myrealm?"'
                response.status = 401
                response.content = ''
            """

            # check HTTP 500 traceback
            if response.status == 500 and response.traceback:
                response.content = response.traceback

            if inspect.isgenerator(response.content):
                content = [row for row in response.content]
            else:
                content = response.content

            # check Content-Length (last modif allowed)
            if is_string(content):
                response.headers['Content-Length'] = len(content)

            # send response
            status = '%s %s' % (response.status, http_responses.get(response.status))

            if response.content_type:
                response.headers['Content-Type'] = response.content_type
            wsgi_response_headers = [(str(k), str(v)) for k, v in list(response.headers.items())]

            # reponse wsgi
            print('status', status)
            start_response(status, wsgi_response_headers)
            if hasattr(content, 'read'):

                content.seek(0)

                if 'wsgi.file_wrapper' in environ:
                    return environ['wsgi.file_wrapper'](content, 1024)
                else:

                    def file_wrapper(fileobj, block_size=1024):
                        try:
                            data = fileobj.read(block_size)
                            while data:
                                yield data
                                data = fileobj.read(block_size)
                        finally:
                            fileobj.close()

                    return file_wrapper(content, 1024)

            elif content != None and not is_string(content):
                content = str(content) if not is_string(content) else content.encode('utf8')
            elif content == None:
                content = ''

            return [_send(content.encode('utf8'))]  # any iterable/yield ?

        except Exception as err:
            # to fix - missing cors header in this case
            print(traceback.format_exc())
            status = '%s %s' % (500, http_responses.get(500))

            res = str(traceback.format_exc()).replace('\n', '<br>').replace('\t', '    ')

            res = """<html><body><h1>%s</h1><h2>%s</h2><p>%s</p></body></html>""" % (status, err, res)
            start_response(status, [('Content-Type', 'text/html')])
            return [_send(res)]


class Httpds(Httpd):

    def run(self):
        from gevent import pywsgi
        keyfile = '/apps/server.key'
        certfile = '/apps/server.crt'
        server = pywsgi.WSGIServer(('0.0.0.0', self.port), self.h, keyfile=keyfile, certfile=certfile)
        print('httpds running...', self.port)
        server.serve_forever()


class HttpsService(HttpService):

    def __init__(self, *args, **kwargs):
        HttpService.__init__(self, *args, **kwargs)
        self.httpd = Httpds(self, self.port)
