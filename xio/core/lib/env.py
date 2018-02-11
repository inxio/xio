#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .utils import urlparse,is_string

import os.path
import inspect
import traceback

class Context(dict):

    def __init__(self, *args, **kwargs):
        super(Context, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattr__(self, name):
        return self.get(name)
        
    def __setattr__(self, name, value):
        super(Context, self).__setattr__(name, value)
        if name=='config':
            self.init()

    def init(self,**config):

        import xio

        config = config or self.config or {}

        # SETUP DEFAULT USER
        id = config.get('id')
        token = config.get('token')
        private_key = config.get('key')

        try:
            self.user = xio.user(id=str(id),token=str(token),key=str(private_key))
        except:
            self.user = xio.user()
        assert self.user.id

        # SETUP DEFAULT XIO ENDPOINT
        network_uri = config.get('network', xioenvdefault.get('network') )
        self.network = xio.network(network_uri)

context = Context()


# environnement 
userhomedir = os.getenv("HOME")
xioenvdir = userhomedir+'/.xio/'
xioenvfilepath = xioenvdir+'user.session'
xioenvdefault = {}
try:
    import json
    if os.path.isdir(xioenvdir):
        if os.path.isfile(xioenvfilepath):
            with open(xioenvfilepath) as f:
                context.config = json.load(f)
except Exception as err:
    pass

def setDefaultEnv(data):
    if not os.path.isdir(xioenvdir):
        os.mkdir(xioenvdir)
    with open(xioenvfilepath,'w') as f:
        json.dump(data, f,  sort_keys=True,indent=4)




def env(key,val=None):
    assert key in ('node','user','network','id','token','log','env') or key.startswith('app_') or key.startswith('node_')
    envkey = 'XIO_%s' % key.upper()
    if val==None:
        return context.get(envkey, os.environ.get(envkey) ) or xioenvdefault.get('xio.'+key)
    elif is_string(val):
        os.environ[envkey] = val  
    else:
        context[envkey] = val






# XRN RESOLVE

__PATH__ = []
__LOCAL_APPS__ = {}


def resolv(uri):
    info = urlparse(uri)
    scheme = info.scheme
    netloc = info.netloc
    path = info.path 

    from xio import handlers
    handler = handlers.get(scheme)

    # handle class and/or function/coroutine
    if inspect.isclass(handler) or inspect.isfunction(handler):
        handler = handler(uri)   
    return (handler,None)    

def getLocalApp(xrn):
    import sys
    import os.path
    import importlib

    #print ('lookup', xrn,'in', __PATH__)

    # step1: recherche locale
    if xrn in __LOCAL_APPS__:
        return __LOCAL_APPS__[xrn]

    for path in __PATH__:
        p = path.split('/')

        dirname = p.pop()

        if os.path.isdir(path):
            for name in os.listdir(path):
                if os.path.isfile(path+'/'+name+'/app.py'):
                    syspath = path
                    sys.path.insert(0,syspath)
                    try:
                        x = xrn.split(':')
                        n = name.replace('_',':')
                        if n in xrn or (len(x)>2 and x[2] in n) or x[2] in n:
                            directory = path+'/'+name
                            if os.path.isdir(directory):
                                modpath = name+'.app'
                                mod = importlib.import_module(modpath,package='.')
                                __LOCAL_APPS__[mod.app.id] = mod.app
                                __LOCAL_APPS__[mod.app.name] = mod.app
                                if xrn in mod.app.id or xrn in mod.app.name:
                                    return mod.app
                    except Exception as err:
                        import xio
                        import traceback
                        xio.log.warning('unable to load',xrn,'from', directory,err)
                        traceback.print_exc()
                    sys.path.remove(syspath)










