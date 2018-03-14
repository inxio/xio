#!/usr/bin/env python
#-*- coding: utf-8 -*--

import xio

import json

from pprint import pprint
import copy


class CacheHandler:

    def __init__(self):
        self.db = xio.db(__name__).container('cache')


    def put(self,index,data):
        meta = data.get('meta')
        content = data.get('content')
        ttl = data.get('ttl')
        meta = meta or {}
        print '>> CacheManager PUT',index, data

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

        data = {
            'content_type': content_type,
            'content': content,
        }
        self.db.put(index,data,ttl=ttl)
        

    def delete(self,index):
        return self.db.delete(index)


    def get(self,index):
        
        print ('>> CacheManager GET', index)
        data = self.db.get(index)
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


        


if __name__=='__main__':


    import unittest


    manager = CacheHandler()

    class Tests(unittest.TestCase):

            
        def test(self):
            print manager.put('someindex',{'title': 'sometitle'})
            print manager.get('someindex')

    unittest.main()





            


