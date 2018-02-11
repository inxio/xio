#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

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

from .handlers import *

from xio.core.lib.request import Request, Response

from xio.core.lib import utils
from xio.core.lib import env

is_string = utils.is_string


from functools import wraps

def client(*args,**kwargs):
    res = resource(*args,**kwargs)
    # todo: setup flags for this client resource (context, _skip_handler_allowed, xmetods, etcc)
    return res

def resource(handler=None,context=None,about=None,**kwargs):
    
    basepath = ''

    if isinstance(handler, Resource):
        handler = pythonResourceHandler(handler)
    elif isinstance(handler, collections.Callable):
        handler = pythonCallableHandler(handler)
    elif handler and ':' in handler:
        handler,basepath = env.resolv(handler) 
    elif handler and is_string( handler ):
        handler = PeerHandler(handler)
    elif handler:
        raise Exception('UNHANDLED RESOURCE HANDLER (%s)' % handler)

    return Resource(handler=handler,handler_path=basepath,handler_context=context,about=about,**kwargs)


def extractAbout(h):
    import yaml
    about = {}
    docstring = h.__doc__ if h and not is_string(h) and isinstance(h, collections.Callable) else h
    if docstring and is_string(docstring): # warning if h is open file !
        try:
            about = yaml.load(docstring) 
            assert isinstance(about,dict)
            version = about.get('version')
            if not version:
                print('DEPRECIATED ABOUT')
                assert 'type' in about or 'implement' in about or 'methods' in about or 'options' in about or 'resources' in about or 'description' or 'cache' in about# a virer !
        except Exception as err:   
            about = {}    

    # fix methods
    about.setdefault('methods',{})
    options = about.pop('options',[])

    assert not isinstance(options,dict) # prevent old versions
    
    if not isinstance(options,list):
        options = [ o.strip().upper() for o in options.split(',') ] 
    if not about['methods']:
        for method in options:
            about['methods'][method] = {}
            if 'input' in about:
                about['methods'][method]['input'] = about['input']
            if 'output' in about:
                about['methods'][method] ['output'] = about['output']

    about['options'] = options

    # clear old params
    about.pop('output',None)
    about.pop('input',None)
    about.pop('method',None)

    return about



def handleRequest(func):
    """
    handle
        -> automatic converion of input to req object
        -> automatic converion of result to res object
        -> prevent req.path modification by handlers
    """

    @wraps(func)
    def _(self,method,*args,**kwargs):

        if not isinstance(method,Request):
            if not args:
                path,data = (None,None)
            elif len(args)==1:
                path,data = (args[0],None) if is_string(args[0]) else (None,args[0])
            elif len(args)==2:
                path,data = args
            else:
                path = args[0]
                data = args[1]

            path = path or ''
            if path and path[0]=='/': 
                path = path[1:]

            kwquery = kwargs.pop('query',None)
            kwdata = kwargs.pop('data',None)       

            if method=='GET':
                query = data or kwquery
                data = None
            else:
                query = kwquery
                data = data or kwdata

            client = self.context.get('client')     
            req = Request(method,path,data=data,query=query,client_context=self._handler_context,client=client,**kwargs)
        else:
            
            req = method
            req._stack.append(self)

        assert req and isinstance(req,Request)
        assert is_string(req.method)

        ori_path = req.path

        # update context
        req.context['resource'] =  self 
        req.context['root'] =  self._root 
        req.context['debug'] = kwargs.get('debug')
        
        if kwargs.get('skiphandler'):
            req.context['skiphandler'] = kwargs.get('skiphandler')

        dbglevel = len(req._stack)    
        try:
            if req.debug:
                print('...' * dbglevel,req)
            resp = func(self,req)
            if req.debug:
                print('...' * dbglevel,resp)
        except Exception as err:
            args = err.args[0].args if err.args and isinstance(err.args[0],Exception) else err.args
            #print('*******',args[0], isinstance(args[0],int) )
            if args and isinstance(args[0],int):
                req.response.status = args[0]
                resp = ' '.join( str(v) for v in args )
            else:
                #traceback.print_exc() 
                req.response.status = 500
                resp = None
            if req.debug:
                print('...' * dbglevel,'ERR',resp)
            #print('*******',req.response.status )      
        if not isinstance(resp, Resource):
            req.path = ori_path
            resp = self._toResource(req,resp) # ,

        assert isinstance(resp, Resource)
        assert not isinstance(resp.content, Resource)
        return resp

    return _


def handleDelegate(func):

    @wraps(func)
    def _(self,req):

        skiphandler = req.context.get('skiphandler') and self._skip_handler_allowed
        must_delegate = self._handler and isinstance(self._handler, collections.Callable) and not skiphandler

        req.response.status = 0

        if must_delegate and req.path:
            c,p,u = self._getChild(req.path)
            must_delegate = not bool(c)

        if must_delegate:
            
            result = self._callhandler(req) 

            req.response.status = req.response.status or 200
            req.response.content = result   # attention car result peux etre une resource

            if req.response.content==req.PASS: # car d'un handler renvoyant vers le handling par defaut
                req.response.status = 0
                req.response.content = None
                    
        return func(self,req)

    return _


class Resource(object):

    __XMETHODS__ = True
    _skip_handler_allowed = True
    _tests = None

    def __init__(self,content=None,path='',status=0,headers=None,parent=None,root=None,handler=None,handler_path=None,handler_context=None,about=None,**context):

        assert not root or isinstance(root,Resource)
 
        self.path = path
        self.content = content
        self.status = status
        self.headers = headers or {}
        self.content_type = self.headers.get('Content-Type')

        self._handler = handler if handler else self.content if self.content and isinstance(self.content, collections.Callable) else None
        self._handler_path = handler_path
        self._handler_context = handler_context
        self._parent = parent
        self._root = root or (parent._root if parent else self)
        self._children =  collections.OrderedDict()
        self._about = extractAbout(about or self._handler or self.content)
        self.context = context


    # HTTP STANDARD METHODS

    def options(self,*args,**kwargs):
        return self.request('OPTIONS',*args,**kwargs)

    def head(self,*args,**kwargs):
        return self.request('HEAD',*args,**kwargs)

    def connect(self,*args,**kwargs):
        return self.request('CONNECT',*args,**kwargs)

    def get(self,*args,**kwargs):
        return self.request('GET',*args,**kwargs)

    def post(self,*args,**kwargs):
        return self.request('POST',*args,**kwargs)

    def put(self,*args,**kwargs):
        return self.request('PUT',*args,**kwargs)

    def patch(self,*args,**kwargs):
        return self.request('PATCH',*args,**kwargs)

    def delete(self,*args,**kwargs):
        return self.request('DELETE',*args,**kwargs)

    # XIO STANDARD METHODS

    def about(self,*args,**kwargs):
        return self.request('ABOUT',*args,**kwargs)

    def api(self,*args,**kwargs):
        return self.request('API',*args,**kwargs)

    def test(self,*args,**kwargs):
        return self.request('TEST',*args,**kwargs)

    def debug(self,show=True):
        result = []
        for key in self._children:
            res = self.get(key)
            result.append(res)
            result += res.debug(show=False)

        if show:
            for res in result:
                cls = res.__class__.__name__
                content = res.content 
                children = res.content
                path = res.path
                colurn = res.path

        return result


    # CORE 

    def _hasabstract(self):

        if self._abstactchildname==None:
            self._abstactchildname==False
            for k,v in list(self._children.items()):   
                if k[0]==':':
                    self._abstactchildname = k

        return self._abstactchildname   

    def _getChild(self,path):

        pathdata = {}
        p = path.split('/')
        childname = p.pop(0)
        postpath = '/'.join(p)
        child = self._children.get(childname)

        if not child:
            for k,v in list(self._children.items()):   
                if k[0]==':':
                    return (v,postpath,{k:childname})   
                    
        return (child,postpath,pathdata)


    def _toResource(self,req,resp,handler_path=None):

        if not isinstance(resp,Response):
            result = resp
            resp = req.response
            resp.content = result    

        if self.path:
            path = self.path+'/'+req.path if req.path else self.path
        else:
            path = req.path

        content = resp.content if resp else None
        status = resp.status if resp else 404

        res = copy.copy(self)
        res.path = path
        res.content = content
        res.content_type = resp.headers.get('Content-Type')
        res.headers = resp.headers
        res.status = status
        res._handler_path = handler_path
        return res


    def resource(self,relativepath,status=200,content=None,headers=None,handler_path=None):
        
        if self.path:
            path = self.path+'/'+relativepath if relativepath else self.path
        else:
            path = relativepath

        headers = headers or {}

        res = copy.copy(self)
        res.path = path
        res.content = content
        res.content_type = headers.get('Content-Type')
        res.headers = headers
        res.status = status
        res._handler_path = handler_path
        return res


    @handleRequest
    @handleDelegate
    def request(self,req):

        assert isinstance(req,Request)
        assert is_string(req.method)

        if req.response.status!=0:
           
            if isinstance(req.response.content,Resource):
                return req.response.content

            handler_path = self._handler_path+'/'+req.path if self._handler_path else req.path
            resp = req.response
        else:
            resp = self._defaultHandler(req)
            handler_path = None

        return resp if isinstance(resp,Resource) else self._toResource(req,resp,handler_path) # put handler_path in response metadata ?



    def _callhandler(self,req):

        ori_path = req.path

        if req.method=='GET' and not req.path and req.query==None:
            return self

        if self._handler_path:
            req.path = self._handler_path+'/'+req.path if req.path else self._handler_path

        # step1 : CHECK ALLOWED METHOD
        options = self._about.get('options',[])
        method = req.xmethod or req.method

        # step2 : fix ABOUT
        if not req.path and req.ABOUT and options and not 'ABOUT' in options:
            return req.PASS

        if not req.path and options:
            assert method in options, Exception(405)

        # step3 : CHECK INPUT
        params = self._about.get('methods',{}).get(method,{}).get('input',{}).get('params',[])
        mapping = {
            'integer': int,
            'float': float,
            #'date': 
        }
        
        for param in params:
            name = param.get('name')
            paramtype = param.get('type')
            required = param.get('required')
            default = param.get('default')
            pattern = param.get('pattern')
            value = req.input.get(name)

            # check required
            assert value or not required, Exception(400,'Missing required parameter : %s' % name)
            # check type
            assert not paramtype or value==None or isinstance(value, mapping.get( paramtype )), Exception(400,'Wrong datatype parameter : %s' % name)
            # check pattern
            if pattern and value:
                import re
                rpattern = re.compile(pattern)
                assert re.match(rpattern,value), Exception(400,'Wrong format parameter : %s' % name)

        result = self._handler(req)  

        req.path = ori_path

        return result
        

    def _defaultHandler(self,req):

        method = req.xmethod or req.method
        path = req.path
        data = req.data

        must_redirect = bool(path) 
        put_context = req.PUT and path and not '/' in path

        if must_redirect: 

            res,postpath,urldata = self._getChild(path) 

            if res==None and method=='PUT' and '/' in path:
                p = path.split('/')
                childname = p.pop(0)
                postpath = '/'.join(p)
                res = self.put(childname)  
            
            if res!=None:

                if isinstance(req.input,dict):
                    req.context.update(urldata)

                req.path = postpath
                return res.request(req)
            else:
                if not put_context:
                    return self.resource(path,content=None,status=404)

        name = path
        assert not'/' in name

        if method=='ABOUT':
            return self._handleAbout(req)

        if method=='TEST':
            return self._handleTest(req)

        elif method=='API':
            return self._handleApi(req)

        elif method=='GET':
            return self

        elif method=='PUT':

            if not name:
                self.content = data
                if isinstance(data, collections.Callable):
                    self._handler = data
                return self

            assert name

            path = self.path+'/'+name if self.path else name
            child = Resource(path=path,content=data,status=201,parent=self) if not isinstance(data,Resource) else data

            self._children[name] = child
            return self._children[name]



    def __getattr__(self, name):
    
        if name[0]!='_':
        
            if self.content and  hasattr(self.content,name):
                return getattr(self.content,name)

            if self.__XMETHODS__:
                setattr(self,name,lambda *args,**kwargs: self.request(name.upper(),*args,data=kwargs) )

        return object.__getattribute__(self, name)


    def __repr__(self):
        return '%s #%s %s %s [%s] %s' %  (self.__class__.__name__.upper() ,id(self), repr(self.path), self._handler or 'nohandler', self.status,str(self.content)[0:50]+'...' )

    def __call__(self,*args,**kwargs):
        return self.content(*args,**kwargs)

    def __iter__(self):
        return iter(self.content)   
 
    def bind(self,*args,**kwargs):
        if len(args)>1:
            path = args[0]
            content = args[1]
            kwargs['skiphandler'] = True
            return self.put(path,content,**kwargs)        
        else:
            def _wrapper(func):
                path = args[0]
                kwargs['skiphandler'] = True
                return self.put(path,func,*args,**kwargs)        
            return _wrapper


    def hook(self,path,*args,**kwargs):

        class _hookwrapper:

            def __init__(self,h,ori):
                self.h = h
                self.ori = ori
               
            def __call__(self,req):
                setattr(req,'hook',self.ori)
                return self.h(req)

        def _(func):
            target = self.get(path) 
            target.content = _hookwrapper( func, target.content )   
            return target

        return _


    def _handleAbout(self,req):

        about = copy.copy(self._about)
        root = req.context.get('root')
        
        peerserver = self._root or req.server or root # tofix root could be None

        fullpath = req.fullpath.replace('/','')

        if fullpath=='www' or fullpath=='':
            about = copy.copy(root._about) if root and root._about else about  
            if peerserver:
                about['id'] = peerserver.id
                about['name'] = peerserver.name  
            about['type'] = self.__class__.__name__.lower() if not peerserver else peerserver.__class__.__name__.lower()
           
        about.setdefault('resources',{})
        
        for childname,child in list(self._children.items()):
            about['resources'][childname] = {}
        
        return about



    def _handleTest(self,req):

        root = req.context.get('root')
        return root._handleTest(req)
        
        if req.fullpath.replace('/','')=='www':
            return root._handleTest(req)

        tests = self._about.get('tests',[])
        results = []
        for test in tests:

            try:
                method = test.get('method','GET')    
                path = test.get('path','')  
                query = test.get('input',{})  
                req = Request(method,path,query=query)
                resp = self.request(req)
                assertions = test.get('assert')    
                assert not assertions.get('content') or (resp.content and str(assertions.get('content')) in str(resp.content) )
                assert not assertions.get('status') or int(assertions.get('status'))==resp.status
                result = {
                    'status': 200,
                }
            except Exception as err:
                result = {
                    'status': 500,
                    'error': err
                }
            results.append(result)

        return results


    def _handleApi(self,req):

        api = collections.OrderedDict()

        about = self.about(req).content

        methods = about.get('methods',{})
        resources = about.get('resources',{})
        description = about.get('description')

        # root route
        info = {}
        if description:
            info['description'] = description

        if methods:
            info['methods'] = collections.OrderedDict()
            for method,methodinfo in list(methods.items()):
                info['methods'][method] = methodinfo

        api['/'] = info

        for childname,info in list(resources.items()):
            childapi = self.api(childname).content or {}
            for cpath,info in list(childapi.items()):
                if cpath[-1]=='/':
                    cpath=cpath[:-1]
                cpath = '/'+childname+cpath
                api[cpath] = info
        return api



    def debug(self):

        res = self

        #from logs import colorize,BLUE,YELLOW,RED,CYAN,GREEN
        RESET_SEQ = "\033[0m"
        COLOR_SEQ = "\033[1;%dm"
        BOLD_SEQ = "\033[1m"
        CODE_BACKGROUND = 40
        CODE_FOREGROUND = 30
        BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = list(range(8))
        BOLD = -1
        def colorize(txt,code,background=False):
            #The background is set with 40 plus the number of the color, and the foreground with 30

            if code==BOLD:
                return BOLD_SEQ + txt + RESET_SEQ
            elif code:

                TYPE = CODE_BACKGROUND if background else CODE_FOREGROUND
                return COLOR_SEQ % (TYPE + code) + txt + RESET_SEQ
            else:
                return txt


        def _map(res,stack):    

            try:

                cls = res.__class__.__name__
                
                content = res.content 
                children = res.content
                    
                if True: #content!=None or isinstance(res,App) or res._children: 
                
                    import inspect

                    if content and inspect.isclass(content):
                        content = colorize(str(content)[0:50],YELLOW)

                    elif content and is_string(content):
                        content = colorize(str(content)[0:50],RED)
                        
                    elif content and isinstance(content, collections.Callable):
                        content = colorize(str(content)[0:50],GREEN)
                    else:
                        content = str(content)[0:50] if content else ''
                        

                    path = []
                    colouredpath = []
                    for k,v in stack:
                        path.append(k)
                        if isinstance(v,Resource):
                            colouredpath.append( colorize(k,BLUE) )
                        else:
                            colouredpath.append( colorize(k,CYAN) )

                    path = '/'.join([v[0] for v in stack])
                    colurn = colorize(path,BLUE)

                    print("\t",colurn,'.'*(60-len(path)),cls.upper()[0:3]+' '+str(id(res))+' %s ' % res.status+' '*(10-len(cls)),content or '')

                
                # child sauf si client.resources
                if isinstance(res,Resource):
                    children = res._children
                    keys = list(children.keys())
                    keys.sort()
                    for name in keys:
                        child = children.get(name)
                        _map(child,stack+[(name,child)])


            except Exception as err:
                print(('\tERR',err,'...',res))
                

        print('\n______ DEBUG ______\n')
        print('\tresource     :',self)
        print('\tpath         :',self.path)
        print('\thandler      :',self._handler)
        print('\thandler_path :',self._handler_path)
        print('\tabout        :',self._about)
        print('\tchildren     :',list(self._children.keys()))
        _map(self,[])
        print('\n______ /DEBUG ______\n')



