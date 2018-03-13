#!/usr/bin/env python
#-*- coding: utf-8 -*--

import xio

import json

from pprint import pprint
import copy



def handleCache(func):

    
    def _(res,req):
        print(('==========> node cache',req, req.response.ttl)) 
        ttl = req.response.ttl
        if ttl: # mise en cache a la demande independament de la methode
            cacheservice = res.get('services/cache') 
            if cacheservice:

                import base64
                import inspect

                query = req.input
                xio_skip_cache = query.pop('xio_skip_cache',None)

                uid = '%s-%s-%s' % (req.fullpath,req.input,req.profile)
                uid = base64.urlsafe_b64encode(uid).strip('=')

                if xio_skip_cache:
                    print((cacheservice.delete(uid)))

                cached = cacheservice.get(uid,{})
                
                if cached and xio_skip_cache==None and cached.status==200:
                    print('found cache !!!')
                    info = cached.content 
                    response = Response(200)
                    response.content_type = info.get('content_type')
                    response.headers = info.get('meta').get('headers')
                    response.headers['xio_cache_ttl'] = info.get('meta').get('ttl') 
                    response.content = info.get('content')
                    return response
                else:
                    result = func(res,req)
                    response = req.response
                    
                    # cas des generateur, on doit pouvoir utiliser du cache mais peux etre trés dangereux !
                    cache_allowed = ttl and bool(response) and response.status==200 and not inspect.isgenerator(response.content)
                    if cache_allowed:
                        print(('write cache !!!', ttl, 'by', res.name))
                        meta = {'headers': dict(response.headers) }
                        cacheservice.put(uid,data={'content':response.content,'ttl':int(ttl),'meta':meta})
                    else:
                        print(('no cachable !!!', ttl, bool(response), response.status))
                    return result

        return func(res,req)

    return _




class CacheManager:

    def __init__(self):
        self.db = xio.db(__name__).container('cache')


    def put(self,index,content=None,ttl=10,meta=None):
        
        meta = meta or {}
        print '>> CacheManager PUT','ttl=',ttl,'PUT',index

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
        
        print '>> CacheManager GET', index
        data = self.db.get(index)
        if data:
            # si 404 => no cache
            print '>>> FOUND CACHE !'
            return data

        


if __name__=='__main__':


    import unittest


    manager = CacheManager()

    class Tests(unittest.TestCase):

            
        def test(self):
            print manager.put('someindex',{'title': 'sometitle'})
            print manager.get('someindex')

    unittest.main()





            


