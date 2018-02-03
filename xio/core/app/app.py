#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from xio.core import resource 
from xio.core import peer

from xio.core.lib.request import Request, Response
from xio.core.lib.logs import log
from xio.core.lib.utils import is_string, urlparse

from xio import path

import os
import posixpath
import sys
import traceback
import time

import importlib
import yaml

import collections

import requests
import json
import base64
import uuid
import inspect
import hashlib
import copy



from pprint import pprint


# to fix etx xio
_extdir = os.path.dirname( os.path.realpath(__file__) )+'/ext'
path.append(_extdir)


def getAppsFromDirectory(path):

    syspath = path
    p = path.split('/')

    apps = []
    sys.path.insert(0,syspath) 
    if os.path.isdir(path):
        for name in os.listdir(path):
            try:
                directory = path+'/'+name
                if os.path.isdir(directory):
                    modpath = name+'.app' 
                    mod = importlib.import_module(modpath,package='.')
                    apps.append( (name,mod.app) )
            except Exception as err:
                import xio
                import traceback
                xio.log.warning('unable to load',name,'from', directory)
                #traceback.print_exc()
    sys.path.remove(syspath) 
    return apps



def app(*args,**kwargs):
    return App.factory(*args,**kwargs)


class App(peer.Peer):

    name = 'lambda'
    module = None
    directory = None
    _about = None
    _skip_handler_allowed = True
    
    def __init__(self,name=None,module=None,**kwargs):

        peer.Peer.__init__(self,**kwargs) 

        self.bind('www', self.render ) 
        
        if module:
            self.module = module
            self.directory = os.path.realpath( os.path.dirname( self.module.__file__ )) if self.module else None
            self.load()

        self.endpoint = None
        self.wsgi_http = None
        self.wsgi_ws = None
        self.log = log

        self.init()

    @classmethod
    def factory(cls,id=None,*args,**kwargs):

        if is_string(id):
            module = sys.modules.get(id) 
            if module:
                return cls(module=module,**kwargs)
                
        return peer.Peer.factory(id,*args,_cls=cls,**kwargs)

    def load(self):
        module = self.module

        # loading ext first because about can refer on
        if os.path.isdir(self.directory+'/ext'):
            import xio
            xio.path.append(self.directory+'/ext')
            for childname,child in getAppsFromDirectory(self.directory+'/ext'):
                child = xio.app(child) 
                self.put('ext/%s' % childname, child ) 


        # loading about.yml
        self._about = {}
        if os.path.isfile(self.directory+'/about.yml'):
            with open(self.directory+'/about.yml') as f:
                self._about = yaml.load(f)

        self.name = self._about.get('name')
        if 'id' in self._about:
            self.id = self._about.get('id')

        # loading test
        if os.path.isfile(self.directory+'/tests.py'):
            try:
                testspath = module.__package__+'.tests' if '.' in module.__name__ else 'tests'
                self._tests = importlib.import_module(testspath)

            except Exception as err:
                log.warning('TEST LOADING FAILED',err)
                self._tests = 'error' 

        # loading www
        """
        wwwdir = self.directory+'/www'
        if os.path.isdir(wwwdir):
            self.bind('www', resource.DirectoryHandler(wwwdir)  )
        """

        wwwstaticdir = self.directory+'/www/static'
        if os.path.isdir(wwwstaticdir):
            self.bind('www/static', resource.DirectoryHandler(wwwstaticdir)  )



    def init(self):

        # scheduler
        from .services.cron import SchedulerService
        self.put('services/cron', SchedulerService(self) )

        # build resources
        if self._about:
            resources = self._about.get('resources')
            if resources and isinstance(resources,dict):
                for path,info in list(self._about.get('resources',{}).items()):
                    handler_class = info.get('handler',None) 
                    handler_path = info.get('path','') 
                    handler_params = info.get('params',{}) 

                    handler_params['xio_id'] =  self.id
                    handler_params['xio_token'] = 'FAKE TOKEN' # tofix 

                    rhandler = client.app(handler_class,handler_params) 
                    rhandler.basepath = handler_path
                    rhandler.profile = handler_params # tofix
                    app.put(path, rhandler )

        # build services
        services = self._about.get('services')
        if services:
            log.info('=== LOADING SERVICES ===')
            for service in services:
                log.info('=== LOADING SERVICE ', service)
                name = service.pop('name')
                handler_class = service.get('handler',None) 
                handler_params = service.get('params',{}) 

                if is_string(handler_class):
                    remotehandler = ':' in handler_class or '/' in handler_class
                    pythonhandler = not remotehandler and '.' in handler_class
                    if remotehandler:
                        assert self.id
                        handler_params['xio_id'] =  self.id
                        handler_params['xio_token'] = 'FAKE TOKEN' # tofix 
                        import xio    
                        servicehandler = None #xio.resource(handler_class,handler_params)
                    else:
                        import importlib
                        p = handler_class.split('.')
                        classname = p.pop() 
                        modulepath = '.'.join(p)     
                        module = importlib.import_module(modulepath)
                        handler_class = getattr(module,classname)
                        servicehandler = handler_class(app=self,**handler_params)

                    self.put('services/%s' % name, servicehandler)



    def schedule(self,*args,**kwargs):

        scheduler = self.get('services/cron')

        if len(args)>1:
            scheduler.schedule(*args,**kwargs)
        else:
            def _wrapper(func):
                c = args[0]
                return scheduler.schedule(c,func,*args[1:],**kwargs)
            return _wrapper


    def render(self,req):
        self.log.info('APP RENDER',req.xmethod or req.method, repr(req.path),'by',self)
        res = self.request(req)
        return res
       


    def run(self,loop=True,port=8080,debug=False,websocket=None):

        self.put('etc/services/http',{'port':int(port)})    
        if websocket:
            self.put('etc/services/ws',{'port':int(websocket)})    
        if debug:
            log.setLevel('DEBUG')

        self.start()
        if loop:    
            import time
            while True:
                time.sleep(0.1)



    def start(self,use_wsgi=False):

        for name,res in list(self.get('etc/services')._children.items()):
            servicehandler = None
            if use_wsgi and name in ['http','https','ws','wss']:
                continue

            conf = copy.copy(res.content) # need to kepp the original config for debug/map

            self.log.info('STARTING SERVICE %s (%s)' % (name,conf))
            
            if not isinstance(conf,dict):
                servicehandler = conf
            else:
                from .services import websocket
                from .services import http

                port = conf.get('port')
                scheme = conf.get('scheme', name)
                options = {}
                path = conf.get('path') 
                if scheme == 'ws':
                    servicehandler = websocket.WebsocketService(app=self,port=port,**options)  
                elif scheme == 'http':
                    servicehandler = http.HttpService(app=self,path=path,port=port,**options)
                elif scheme == 'https':
                    servicehandler = http.HttpsService(app=self,path=path,port=port,**options)

            if servicehandler:
                servicehandler.start()
                self.put('run/services/%s' % name, servicehandler)




    def __call__(self,environ,start_response=None): 

        # handle app as handler
        if isinstance(environ,Request):
            req = environ
            return self.request(req)


        # init wsgi handler(s)

        if not self.wsgi_http:
        
            from .services import http
            self.wsgi_http = http.HttpService(app=self,context=environ)

            from .services import websocket
            self.wsgi_ws = websocket.WebsocketService(app=self,context=environ)

            import gevent
            gevent.spawn(self.start,use_wsgi=True)
            

        # select handler
        handler = self.wsgi_http
        if environ.get('HTTP_CONNECTION')=='Upgrade' and environ.get('HTTP_UPGRADE')=='websocket' and environ.get('HTTP_SEC_WEBSOCKET_KEY'):
            handler = self.wsgi_ws
        
        # handle
        try:
            return handler(environ,start_response)
        except Exception as err:
            import traceback
            traceback.print_exc()
            start_response('500 ERROR',[('Content-Type','text')])
            return [ str(traceback.format_exc()) ]

  

    def main(self):
    
        import sys
        import os
        from pprint import pprint
        import os.path
        import xio

        args = sys.argv

        args = args+[None]*5
        param0 = args[0]
        cmd = args[1]
        param1 = args[2]
        param2 = args[3]
        param3 = args[4]
        param4 = args[5]

        print('\n\n==========',cmd, param1 or '')
        print("""
            map:        app map
            run:        run services on debug mod
            *:          HTTP * ( www/* )
        """)    
        print()
        print("\tapp=",self)
        print("\tapp=",self.id)
        print('\tapp=',self.name)
        print('\tapp=',self._about)
        print('\tnode=',xio.env('node'))
        print()

        if cmd=='run':

            import optparse
            parser = optparse.OptionParser()

            parser.add_option("-p", "--port",help="Port for the app [default 8080]",default=8080)
            parser.add_option("-d", "--debug",action="store_true", dest="debug",help=optparse.SUPPRESS_HELP)
            parser.add_option("-w", "--websocket",help="Port for the websocket [default 8484]",default=None)
            parser.add_option("-n", "--node",help="xio node [default localhost:8080]",default='local')
            
            options, _ = parser.parse_args()  

            self.run(port=options.port,debug=options.debug,websocket=options.websocket)
            import time
            while True:
                time.sleep(0.1)
            sys.exit()    
        if cmd:
            method = cmd.upper()

            h = self.get('bin/%s' % cmd)
            if h.content:
                print('=====> bin', cmd,  h.content, args[2:])
                res = h(xio.request('POST','',data={'args':args[2:]}))
                pprint(res)
            else:

                path = param1 or ''

                h = getattr(self,method)
                res = h(path)
                print(type(res.content))
                print() 
                print('_'*30)
                print()
                print('\trequest:\t',method,repr(path or '/'))
                print('\tresponse:\t', res)
                print('\tresponse code:\t', res.status)
                print('\tresponse headers:\t')
                for k,v in list(res.headers.items()):
                    print('\t\t',k,':',v)
                print('\tresponse type:\t', res.content_type)
                print('\tcontent:\t', res.content) 
                print()

                if isinstance(res.content,list) or isinstance(res.content,dict) :
                    pprint(res.content)
                else:
                    print(str(res.content)[0:500])

                print() 

        else:
            all = ('all' in (str(args)))
            self.debug()


        




