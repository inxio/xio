#!/usr/bin/env python
#-*- coding: utf-8 -*--

from .python import Database as PythonDatabase
from .python import Container as PythonContainer

import os.path


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
        self.filepath = db.directory+'/%s.json' % name
        if not os.path.isfile(self.filepath):
            with open(self.filepath,'w') as f:
                f.write('ok')
        self.name = name
        self.data = {}

