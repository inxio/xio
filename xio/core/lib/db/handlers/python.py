#!/usr/bin/env python
#-*- coding: utf-8 -*--



class Database:

    def __init__(self,name,params=None):
        self.name = name
        self.containers = {}

    def list(self):
        return [ Container(key) for key in self.containers ]

    def get(self,name):
        return self.containers.get(name)

    def put(self,name):
        self.containers[name] = Container(name) 
        return self.containers[name]


class Container:

    def __init__(self,name):
        self.name = name
        self.data = {}

    def get(self,index):
        return self.data.get(index)

    def put(self,index,data):
        self.data[index] = data

    def update(self,index,data):
        self.data[index].update(data)

    def truncate(self):
        self.data = {}

    def select(self,filter=None,**kwargs):
        
        # apply filter here
        for row in self.data.values():
            if filter:
                ok = [ row.get(k)== v for k,v in filter.items() ]
                if all(ok):    
                    yield row
            else:
                yield row

    def count(self,**kwargs):
        return len(self.data)

    def delete(self,index,**kwargs):
        del self.data[index]


        
