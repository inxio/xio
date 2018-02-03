#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from pprint import pprint
import time

import xio

from .handlers import python

__HANDLERS__ =  {
    'python': python.Database
}

__DATABASES__ = {}





def db(name=None,type='python',params=None):
    cls = __HANDLERS__.get(type)
    assert cls
    params = params or {}
    return Db(name,cls,params) 



class Db:

    def __init__(self,name,cls,params,containers=None,**kwargs):
        self.name = name
        self.handler = cls(name,params) 

    def list(self):
        return self.handler.list()
        
    def head(self,name):
        return bool(self.get(name))

    def get(self,name):
        chandler = self.handler.get(name)
        return Container( self, chandler) if chandler else None

    def container(self,name):
        container = self.get(name)
        if not container:
            container = self.put(name)
        return container


    def put(self,name):
        # check 409
        exist = self.head(name)
        assert not exist, Exception(409)
        chandler = self.handler.put(name)
        return Container(self,chandler)

    def delete(self,name):
        # prevent not empty container deletion
        count = self.get(name).count()
        assert count==0, Exception(409) 
        log.info('DELETE CONTAINER %s' % name)
        self.handler.delete(name)


class Container:


    def __init__(self,db,handler):
        self.db = db
        self.handler = handler
        self.name = handler.name

    def head(self,id):
        return self.handler.exist(id)

    def get(self,id,fields=None):
        assert id
        data = self.handler.get(id)
        return xio.data(data,fields=fields)
  
    def select(self,filter=None,fields=None,limit=None,start=0,sort=None,**kwargs):
        data = self.handler.select(filter=filter,fields=fields,limit=limit,start=start,sort=sort)
        return xio.data(data,filter=filter,fields=fields)

    def put(self,index,data,ttl=None):
        data['_id'] = index
        data['_created'] = int(time.time()) 
        if ttl:
            data['_ttl'] = ttl         
        self.handler.put(index,data)
        return True


    def update(self,index,data,ttl=None):
        data['_updated'] = int(time.time()) 
        if ttl:
            data['_ttl'] = ttl    
        self.handler.update(index,data)
        return True


    def delete(self,index=None,filter=None):
        # get old value for trigger ops
        deleted_item = self.get(index)
        assert deleted_item,404
        self.handler.delete(index=index,filter=filter)
        return True


    def truncate(self):
        return self.handler.truncate()

    def count(self,**kwargs):
        return self.handler.count(**kwargs)





