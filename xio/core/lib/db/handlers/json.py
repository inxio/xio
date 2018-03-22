#!/usr/bin/env python
#-*- coding: utf-8 -*--

from __future__ import absolute_import

from .python import Database as PythonDatabase
from .python import Container as PythonContainer

import os.path

import json


class Database(PythonDatabase):

    def __init__(self,name,params=None):
        self.name = name
        self.containers = {}
        self.directory = '/tmp'
        
    def list(self):
        return [ Container(self,key) for key in self.containers ]

    def put(self,name):
        self.containers[name] = Container(self,name) 
        return self.containers[name]


class Container(PythonContainer):

    def __init__(self,db,name):
        self.name = name
        self.filepath = db.directory+'/%s.json' % name
        if not os.path.isfile(self.filepath):
            with open(self.filepath,'w') as f:
                json.dump(dict(),f)
                
        with open(self.filepath) as f:
            self.data = json.load(f)
               
    def put(self,*args,**kwargs):
        PythonContainer.put(self,*args,**kwargs)
        self.commit()

    def update(self,*args,**kwargs):
        PythonContainer.update(self,*args,**kwargs)
        self.commit()

    def truncate(self,*args,**kwargs):
        PythonContainer.truncate(self,*args,**kwargs)
        self.commit()
        
    def delete(self,*args,**kwargs):
        PythonContainer.delete(self,*args,**kwargs)
        self.commit()

    def commit(self):
        with open(self.filepath,'w') as f:
            json.dump(self.data,f, indent=4) #sort_keys=True,


        




