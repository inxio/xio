#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import xio
import sys

from pprint import pprint

"""
app = xio.app(lambda req:'ok' )
app.debug()

print app.get('www/hello')
print app.render('GET','hello')


sys.exit()
"""

class TestCases(unittest.TestCase):


    def test_service_pubsub(self):

        results = []

        app = xio.app()
        app.subscribe('topic1',lambda x: results.append(x) )
        app.publish('topic1','some message')
        app.publish('topic1','some message2')
        
        assert len(results)==2


    def test_service_pubsub2(self):

        results = []

        app = xio.app()
        @app.bind('www/path/subpath')
        def _(req):
            # warning req.context.get('resource').path est faux !!! manque www/
            req.context.get('resource').publish('respond request %s' % req.method)
            return 'ok'

        app.debug()
            
        app.subscribe('www/path/subpath',lambda x: results.append(x) )
        
        app.get('www/path/subpath')
        app.get('www/path/subpath')
                
        assert len(results)==2

    def test_service_quota(self):

        # default stats 
        """
        app = xio.app()
        for i in range(1,10):
            app.get('www/somepath')
            assert app.get('services/stats').count(path='somepath').content == i
        """

        # on-demand stats : stat request only if request handler require quota (perf safe)
        app = xio.app()
        app.put('www', lambda req: req.require('quota',2) )
        assert app.get('www').status == 200
        assert app.get('www').status == 200
        assert app.get('www').status == 429


    def test_service_cache(self):
        """
        pb with cache on 'www'
        """

        # default stats 
        app = xio.app()
        @app.bind('www/test1')
        def _(req):
            import random
            req.response.ttl = 2
            return random.random() 
        
        r1 = app.render('test1').content
        r2 = app.render('test1').content
        assert r1==r2


if __name__ == '__main__':

    unittest.main()












  





