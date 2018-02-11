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
    from Cookie import SimpleCookie
else:
    import http.client
    from http.cookies import SimpleCookie
    import urllib.error 

    

def is_string(s):
    try:
        return isinstance(s, basestring)
    except NameError:
        return isinstance(s, str)



class Httpd(threading.Thread):

    def __init__(self,h,port):
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

    def __init__(self,app=None,path='',endpoint=None,port=8080,context=None):
        self.app = app
        self.path = path
        assert self.app!=None
        self.endpoint = endpoint
        self.port = port
        self.context = context
        self.httpd = Httpd(self,port)

    def start(self):
        self.httpd.start()

    def stop(self):
        self.httpd.stop()

    def __call__(self,environ,start_response=None):

        try:
            method = environ.get('REQUEST_METHOD','GET')
            path = environ.get('PATH_INFO','/')
            if path[0]!='/':
                path = '/404'

            query = {}
            for k,v in list(parse_qs(environ.get('QUERY_STRING','')).items()):
                query[k] = v[0] if len(v)==1 else v

            headers = {}
            for k,v in list(environ.items()):
                # warning headers with _ are filtered by wsgi !
                # we re unable to rtreive the original name 
                if k.startswith('HTTP_'):
                    headers[ k[5:].lower() ] = v  
                elif k=='CONTENT_TYPE':
                    # fix content_type 
                    headers[ k.lower() ] = v  


            post_params = {}
            post_data = None

            if method in ('PUT','POST','PATCH'):
            
                import cgi
                post_input = environ.get('wsgi.input') 
                fs = cgi.FieldStorage(environ['wsgi.input'],environ=environ,keep_blank_values=True)

                if not fs.list:
                    post_data = fs.value
                    if headers.get('content_type')=='application/json':
                        import json
                        post_data = json.loads(post_data)
                else:
                    for key in fs:
                        val = fs[key]
                        if val.filename:
                            import tempfile
                            tmpfile = tempfile.TemporaryFile('w')
                            tmpfile.write(val.file.read())
                            post_params[key] = (tmpfile,val.filename)
                        else:
                            post_params[key] = urllib.parse.unquote_plus(val.value) 

                    post_data = post_params


            context = environ


            # cookies handling
            cookies = {}
            cookie_string = environ.get('HTTP_COOKIE')
            if cookie_string:
                c = SimpleCookie()
                c.load(cookie_string)    
                for k,v in list(c.items()):
                    cookies[k] = v.value
            context['cookies'] = cookies
            context['cookies_debug'] = environ.get('HTTP_COOKIE')

            # set context

            pathinfo = environ.get('PATH_INFO')
            
            path = self.path+path if self.path else path
            path = 'www'+path if path else 'www'   

            import xio
            request = xio.request(method,path,headers=headers,query=query,data=post_data,context=context)

            response = self.app.request(request)

            import inspect
            import json
            if isinstance(response.content, dict) or isinstance(response.content, list) or inspect.isgenerator(response.content):
                if inspect.isgenerator(response.content):
                    response.content = [ r for r in response.content ] 
                response.content_type = 'application/json'
                response.content = json.dumps(response.content,indent=4,default=str) 

            # add header Access-Control-Allow-Origin => to fix
            response.headers['Access-Control-Allow-Origin'] = '*'
            if request.OPTIONS:
                response.headers['Access-Control-Allow-Methods'] = 'GET,HEAD,OPTIONS,POST,PUT,PATCH,DELETE,CONNECT'
                response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Content-Length, Date, Accept, Authorization, XIO-id, XIO-token, XIO-view, XIO-method, XIO-profile'

            import inspect

            if inspect.isgenerator(response.content):
                content = [ row for row in response.content ]
            else:
                content = response.content

            if response.status == 403:
                response.headers['WWW-Authenticate'] = 'Basic realm="myrealm"'
                response.status = 401 
                response.content = ''

            # check Content-Length (last modif allowed)
            if is_string(response.content):
                response.headers['Content-Length'] = len(response.content)

            # send response
            status = '%s %s' % (response.status, httplib.responses.get(response.status))
          
            response.headers['Content-Type'] = response.content_type
            wsgi_response_headers = [ (str(k),str(v)) for k,v in list(response.headers.items()) ]
            
            # reponse wsgi
            start_response(status, wsgi_response_headers)
            if hasattr(content, 'read'): 
            
                content.seek(0)

                if 'wsgi.file_wrapper' in environ:
                    return environ['wsgi.file_wrapper'](content,1024) 
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

            elif content!=None and not is_string(content):
                content = str(content) if not is_string(content) else content.encode('utf8')
            elif content==None:
                content = ''

            print ('http content', type(content))     

            return [ content.encode('utf8') ] # any iterable/yield ?

        except Exception as err:
            print(traceback.format_exc())    
            status = '%s %s' % (500, httplib.responses.get(500))
            
            res = str(traceback.format_exc()).replace('\n','<br>').replace('\t','    ')
            
            res = """<html><body><h1>%s</h1><h2>%s</h2><p>%s</p></body></html>""" % (status,err,res)
            start_response(status,[('Content-Type','text/html')])
            return [ res ]


class Httpds(Httpd):
  
    def run(self):
        from gevent import pywsgi
        keyfile='/apps/server.key'
        certfile='/apps/server.crt'
        server = pywsgi.WSGIServer(('0.0.0.0', self.port), self.h, keyfile=keyfile, certfile=certfile)
        print('httpds running...', self.port)
        server.serve_forever()


class HttpsService(HttpService):

    def __init__(self,*args,**kwargs):
        HttpService.__init__(self,*args,**kwargs)
        self.httpd = Httpds(self,self.port)





