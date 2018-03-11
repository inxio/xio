#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
dependencies:
    python: redis


https://redis-py.readthedocs.org/en/latest/


pubsub
https://gist.github.com/jobliz/2596594
"""

import xio




import redis

import json


########## gestion database

class Database:
    
    def __init__(self,name=None,host='localhost',port='??',app=None,**kwargs):
        name = name or app.name
        self.name = name.replace('.','_') # name sera souvent le domain de l'app
        self.port = port
        self.host = host
        self.db = redis.Redis(self.host)

    def get(self,name,**kwargs):
        name = '%s/%s' % (self.name,name)
        return RedisDbContainer(name,self.db)


class Container:

    def __init__(self,name,db):
        self.name = name
        self.db = db

    def get(self,uid,**kwargs):
        key = '%s/%s' % (self.name,uid)
        print 'redis getting ... ', key
        data = self.db.get(key)
        try:
            return json.loads(data)
        except Exception,err:
            print 'REDIS GET ERROR', err  
            return {}

    def put(self,uid,data,**kwargs):
        key = '%s/%s' % (self.name,uid)
        print 'redis put... ', key,' = ',data
        data['_id'] = uid
        data = json.dumps(data)
        return self.db.set(key,data)

    def update(self,uid,data,**kwargs):
        key = '%s/%s' % (self.name,uid)
        data['_id'] = uid
        data = json.dumps(data)
        return self.db.set(key,data)

    def delete(self,index=None,filter=None,**kwargs):
        if filter:
            for row in self.select(filter):
                self.delete(row.get('_id'))
            return
        key = '%s/%s' % (self.name,index)
        return self.db.delete(key)

    def truncate(self):
        for key in self.db.keys(self.name+'/*'):
            self.db.delete(key)

    def select(self,filter=None,limit=20,**kwargs):
        #self.truncate()
        def _check(row):

            if filter:
                for k,v in filter.items():
                    value = row.get(k)
                    if not isinstance(v,list) and value!=v:
                        return False
                    elif isinstance(v,list) and value not in v:
                        return False
            return True

        print 'redis select ...',self.name, filter
        pattern = self.name+'/*'
        data = []
        for key in self.db.keys(pattern=pattern):
            row = self.db.get(key) 
            row = json.loads(row)

            if _check(row):
                data.append( row )
                
            if len(data)>=limit:
                return data

        return data
        
    

