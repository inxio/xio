#!/usr/bin/env python
#-*- coding: utf-8 -*--

import xio

import json

from pprint import pprint
import copy
import time

class PythonHandler:
    
    def __init__(self):
        self.data = {}

    def put(self,index,data,content,ttl):
        data['_created'] = int(time.time())
        data['_expire'] = data['_created'] + ttl    
        data['content'] = content
        self.data[index] = data

    def get(self,index):
        data = self.data.get(index)
        if data:
            expire = data.get('_expire')
            data['ttl'] = expire - int(time.time()) 
            return data

class RedisHandler:

    def __init__(self,redis):
        self.redis = redis
    
    def put(self,index,meta,content,ttl):
        index = 'xio:cache:%s' % index
        print(index,ttl)
        self.redis.hset(index,'meta', json.dumps(meta,default=str) )
        self.redis.hset(index,'content',content)
        self.redis.expire(index,ttl)

    def get(self,index):
        index = 'xio:cache:%s' % index
        cached = self.redis.hgetall(index)
        if cached:
            content_type = cached.get('content_type')
            content = cached.get('content')
            content = json.loads( content ) if content_type=='application/json' else content
            data = json.loads( cached.get('meta') ) 
            data['ttl'] = self.redis.ttl(index)
            data['content'] = content
            return data


__HANDLERS__ =  {
    'python': PythonHandler,
    'redis': RedisHandler,
}




class CacheService:


    def __init__(self,app=None,type='auto'):

        if type=='auto':
            type = 'redis' if app.redis else 'python'

        handlercls =  __HANDLERS__.get(type)
        if type=='redis': # need to pass redis global instance => to fix use params of service and/or use /services/dbmem
            print (app.redis)
            self.handler = handlercls(app.redis)
        else:
            self.handler = handlercls()


    def put(self,index,data):

        print ('put cache')

        content = data.pop('content')
        content_type = data.get('content_type')
        ttl = data.get('ttl')
        
        if isinstance(content,dict) or isinstance(content,list):
            content_type = 'application/json'
            storedcontent = json.dumps(content,indent=4,default=str)
        elif hasattr(content,'read'):
            content_type = 'binary' # to fix
            storedcontent = content.read()
            content.seek(0) 
        else: 
            content_type = 'text'
            storedcontent = content

        meta = {
            'content_type': content_type,
        }
        self.handler.put(index,meta,storedcontent,ttl)
        

    def delete(self,index):
        return self.handler.delete(index)


    def get(self,index):
        
        print ('>> CacheManager GET', index)
        data = self.handler.get(index)
        if data:
            print ('>>> FOUND CACHE !',data)
            return data


    def __call__(self,req):

        if req.path:

            if req.GET:
                return self.get(req.path)

            elif req.PUT:
                return self.put(req.path,req.data)

            elif req.DELETE:
                return self.delete(req.path)




if __name__ == '__main__':

    cache = CacheService(type='redis')
    cache.put('test',{
        'content': 'ok',
        'ttl': 3600
    })

    time.sleep(3)



            


