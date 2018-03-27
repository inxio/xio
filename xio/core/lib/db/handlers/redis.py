#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
dependencies:
    python: redis


https://redis-py.readthedocs.org/en/latest/


pubsub
https://gist.github.com/jobliz/2596594
"""
from __future__ import absolute_import
import xio




import redis

import json


########## gestion database

class Database:
    
    def __init__(self,name=None,host='localhost',port='??',app=None,**kwargs):
        name = name or app.name
        self.name = name.replace('.','_') 
        self.port = port
        self.host = host
        self.db = redis.Redis(self.host) if self.host else redis.Redis()

    def get(self,name,**kwargs):
        name = '%s:%s' % (self.name,name)
        return Container(name,self.db)
        
    def list(self):
        pattern = self.name+':*'
        data = []
        for key in self.db.keys(pattern=pattern):
            data.append(key)
        return data

class Container:

    def __init__(self,name,db):
        self.name = name
        self.db = db

    def get(self,uid,**kwargs):
        key = '%s:%s' % (self.name,uid)
        print ('redis getting ... ', key)
        data = self.db.get(key)
        if data:
            return json.loads(data)
                

    def put(self,uid,data,**kwargs):
        key = '%s:%s' % (self.name,uid)
        print ('redis put... ', key,' = ',data)
        data['_id'] = uid
        data = json.dumps(data,default=str)
        return self.db.set(key,data)

    def update(self,uid,data,**kwargs):
        print ('redis update... ', uid,' = ',data)
        key = '%s:%s' % (self.name,uid)

        oridata = self.get(uid)
        if oridata:
            print ('redis update... ', key,' = ',data)
            oridata.update(data)
            
            data = oridata
            data['_id'] = uid
            data = json.dumps(data,default=str)
            return self.db.set(key,data)

    def delete(self,index=None,filter=None,**kwargs):
        if filter:
            for row in self.select(filter):
                self.delete(row.get('_id'))
            return
        key = '%s:%s' % (self.name,index)
        return self.db.delete(key)

    def truncate(self):
        for key in self.db.keys(self.name+':*'):
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

        print ('redis select ...',self.name, filter)
        pattern = self.name+':*'
        data = []
        for key in self.db.keys(pattern=pattern):
            row = self.db.get(key) 
            row = json.loads(row)

            if _check(row):
                data.append( row )
                
            if data and limit and len(data)>=limit:
                return data

        return data
        
    

