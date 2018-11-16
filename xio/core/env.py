#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .lib.utils import urlparse, is_string

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
        if name == 'config':
            self.init()

    def init(self, **config):

        import xio

        config = config or self.config or {}
        try:
            # SETUP DEFAULT USER
            id = config.get('id')
            token = config.get('token')
            private_key = config.get('key')

            try:
                self.user = xio.user(id=str(id), token=str(token), key=str(private_key))
            except:
                self.user = xio.user()
            assert self.user.id

            # SETUP DEFAULT XIO ENDPOINT
            network_uri = config.get('network') or env.get('network') or xioenvdefault.get('network')
            node_uri = config.get('node') or env.get('node') or xioenvdefault.get('node')
            uri = node_uri or network_uri
            self.network = xio.network(uri) if uri else None
        except Exception as err:
            pass

context = Context()


# environnement
userhomedir = os.getenv("HOME")
xioenvdir = userhomedir + '/.xio/'
xioenvfilepath = xioenvdir + 'user.session'
xioenvdefault = {}
try:
    import json
    if os.path.isdir(xioenvdir):
        if os.path.isfile(xioenvfilepath):
            with open(xioenvfilepath) as f:
                xioenvdefault = json.load(f)
                context.config = xioenvdefault
except Exception as err:
    pass


def getDefaultEnv():
    return xioenvdefault


def setDefaultEnv(data):
    if not os.path.isdir(xioenvdir):
        os.mkdir(xioenvdir)
    with open(xioenvfilepath, 'w') as f:
        json.dump(data, f,  sort_keys=True, indent=4)


class Env:

    def load(self,filepath):
        """
        load from .env file
        """
        # handler env file
        with open(filepath) as f:
            for row in f.readlines():
                if row and row.strip() and '=' in row and row.strip().startswith('XIO_'):
                    try:
                        nfo = row.split('=')
                        key = nfo.pop(0).strip()
                        val = '='.join(nfo).strip()
                        if val and val[0]==val[-1] and val[0]in("'",'"'):
                            val = val[1:-1]
                        self.set(key[4:], val)
                    except:
                        print('ENV FILE ERROR', row)

    def items(self):
        for key, val in context.items():
            if key.startswith('XIO_'):
                yield (key[4:].lower(), val)

    def get(self, name, default=None):
        envkey = 'XIO_%s' % name.upper()
        value = context.get(envkey, os.environ.get(envkey)) or xioenvdefault.get('xio.' + name)
        if value == None:
            return default
        return value

    def set(self, name, value):
        envkey = 'XIO_%s' % name.upper()
        context[envkey] = value
        #
        # if is_string(value):
        #    os.environ[envkey] = value

env = Env()


# XRN RESOLVE

__PATH__ = []
__LOCAL_APPS__ = {}


def register(xrn, app):
    assert xrn.startswith('xrn:')
    print('..registering local app', xrn, app)
    __LOCAL_APPS__[xrn] = app


def resolv(uri):
    if uri in __LOCAL_APPS__:
        return (__LOCAL_APPS__.get(uri), None)

    info = urlparse(uri)
    scheme = info.scheme
    netloc = info.netloc
    path = info.path

    from xio import handlers
    handler = handlers.get(scheme)

    # handle class and/or function/coroutine
    if handler and (inspect.isclass(handler) or inspect.isfunction(handler)):
        handler = handler(uri)

    return (handler, None)


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
                if os.path.isfile(path + '/' + name + '/app.py'):
                    syspath = path
                    sys.path.insert(0, syspath)
                    try:
                        x = xrn.split(':')
                        n = name.replace('_', ':')
                        if n in xrn or (len(x) > 2 and x[2] in n) or x[2] in n:
                            directory = path + '/' + name
                            if os.path.isdir(directory):
                                modpath = name + '.app'
                                mod = importlib.import_module(modpath, package='.')
                                __LOCAL_APPS__[mod.app.id] = mod.app
                                __LOCAL_APPS__[mod.app.name] = mod.app
                                if xrn in mod.app.id or xrn in mod.app.name:
                                    return mod.app
                    except Exception as err:
                        import xio
                        import traceback
                        xio.log.warning('unable to load', xrn, 'from', directory, err)
                        traceback.print_exc()
                    sys.path.remove(syspath)
