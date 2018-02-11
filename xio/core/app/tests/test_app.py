#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import xio
import sys

from pprint import pprint

class TestCases(unittest.TestCase):

    def test_base(self):
    
        app = xio.app()
        assert app.about().content.get('id')==app.id
        app.put('www', lambda req: 'ok' if req.GET else req.PASS)
        assert app.about().content.get('id')==app.id
        assert app.about('www').content.get('id')==app.id
        assert app.request('ABOUT','www').content.get('id')==app.id

        cli = xio.resource(app)
        assert cli.about().content.get('id')==app.id
        assert cli.request('ABOUT','').content.get('id')==app.id

    def test_app_server_lambda(self):

        app = xio.app()
        app.put('www', lambda req: 'ok' if req.GET else req.PASS)
        app.put('www/test', lambda req: 'test')

        assert app.get('www').status==200 and app.get('www').content=='ok' 
        assert app.get('www/test').status==200 and app.get('www/test').content=='test' 

        www = app.get('www')
        assert www.status==200 and www.content=='ok' 
        assert www.get('test').status==200 and www.get('test').content=='test' 

        # alternate (skip handler)
        app = xio.app()
        app.bind('www', lambda req: 'ok')
        app.bind('www/test', lambda req: 'test')
        assert app.get('www').content=='ok' 
        assert app.get('www/test').content=='test' 

        # check client wrapping
        client = xio.app(app)
        assert client.request('GET').content=='ok' 
        assert client.request('GET','test').content=='test' 


    def _test_app_server_module(self):

        from .apptest.app import app 

        assert app

        # test www directory
        #assert app.get('www/index.html').content.read().strip() == 'INDEX'
        assert app.get('www/test1').content == 'ok test1'


        # test ext chainage app/res/app/res
        assert app.get('ext/appext').content == 'ext ok www'
        r1 = app.get('ext/appext/test').content 
        r2 = app.get('ext/appext').get('test').content
        r3 = app.get('ext').get('appext').get('test').content
        r4 = app.get('ext').get('appext/test').content
        assert r1 == r2 == r3 == r4 == 'ext ok test' 


   
    def test_app_about(self):

        app1 = xio.app()
        app1.id = 'ID01'
        #app1._about = {'name':'xrn:xio:app1','id':'ID01'}
        app1.put('www', lambda req: 'OKAPP1' if req.GET else req.PASS)

        client = xio.app(app1)
        assert client.about().content['id']=='ID01'

        a1 = app1.about('www').content
        a2 = app1.request('ABOUT','www').content
        a3 = client.about().content
        a4 = client.request('ABOUT').content

        assert a1['id'] == a2['id'] == a3['id'] == a4['id']


    def test_app_cient_package(self):
        # client can not access to private resources : only www resources are allowed

        from .apptest.app import app 

        app = xio.app( app )

        assert app
        assert app.get('test1').status == 200
        assert app.get('test1').content == 'ok test1'


    def _test_app_ext(self):
        
        from .apptest.app import app 

        # xio ext 
        assert xio.app('xrn:xio:admin')

        # app ext
        assert xio.app('xrn:xio:appext')
        assert app.get('ext/appext').content



    def _test_app_services(self):
        
        from .apptest.app import app 
        ext1 = app.get('services/ext1')

        assert ext1.status==200
        assert ext1.content=='ext ok www'
        assert ext1.get().content=='ext ok www'
        assert ext1.get('test').content=='ext ok test'

        # seamless 
        assert app.get('services/ext1').content == 'ext ok www'
        assert app.get('services/ext1/test').content == 'ext ok test'


    def _test_app_tests(self):
        
        from .apptest.app import app 

        testresult = app.test().content
        assert testresult['qos'] == 66


                        
    def test_app_handler_path(self):

        app = xio.app()
        app.put('www', lambda req: req.path)

        assert app.get('www/test1')._handler_path == 'test1'

        # check public resources path
        assert app.get('www').content==''
        assert app.get('www/test1').content=='test1'
        assert app.get('www/test1/test2').content=='test1/test2'
        assert app.get('www').get('test1').get('test2').content=='test1/test2'

        # check using client wrapper => same behaviour except /www hbase path andling 
        client = xio.app(app)
        assert client.get('').content==''
        assert client.get('test1').content=='test1'
        assert client.get('test1/test2').content=='test1/test2'
        assert client.get('test1').get('test2').content=='test1/test2'


    def test_app_routing(self):

        app = xio.app()
        app.bind('www', lambda req: '%s' % req.method)
        app.bind('www/:container', lambda req: '%s %s' % (req.method,req.context.get(':container')) )
        app.bind('www/:container/:id',lambda req: '%s %s %s' % (req.method,req.context.get(':container'),req.context.get(':id')) )

        # direct
        assert app.get('www').content=='GET'
        assert app.get('www/1234').content=='GET 1234'
        assert app.get('www/1234/5678').content=='GET 1234 5678'
        assert app.post('www').content=='POST'
        assert app.post('www/1234').content=='POST 1234'
        assert app.post('www/1234/5678').content=='POST 1234 5678'
        assert app.put('www').content=='PUT'
        assert app.put('www/1234').content=='PUT 1234'
        assert app.put('www/1234/5678').content=='PUT 1234 5678'

        # by request
        assert app.request('GET','www').content=='GET'
        assert app.request('GET','www/1234').content=='GET 1234'
        assert app.request('GET','www/1234/5678').content=='GET 1234 5678'
        assert app.request('POST','www').content=='POST'
        assert app.request('POST','www/1234').content=='POST 1234'
        assert app.request('POST','www/1234/5678').content=='POST 1234 5678'
        assert app.request('PUT','www').content=='PUT'
        assert app.request('PUT','www/1234').content=='PUT 1234'
        assert app.request('PUT','www/1234/5678').content=='PUT 1234 5678'

        # by client
        client = xio.app(app)

        assert client.get('').content=='GET'
        assert client.get('1234').content=='GET 1234'
        assert client.get('1234/5678').content=='GET 1234 5678'
        assert client.post('').content=='POST'
        assert client.post('1234').content=='POST 1234'
        assert client.post('1234/5678').content=='POST 1234 5678'
        assert client.put('').content=='PUT'
        assert client.put('1234').content=='PUT 1234'
        assert client.put('1234/5678').content=='PUT 1234 5678'

        assert client.request('GET','').content=='GET'
        assert client.request('GET','1234').content=='GET 1234'
        assert client.request('GET','1234/5678').content=='GET 1234 5678'
        assert client.request('POST','').content=='POST'
        assert client.request('POST','1234').content=='POST 1234'
        assert client.request('POST','1234/5678').content=='POST 1234 5678'
        assert client.request('PUT','').content=='PUT'
        assert client.request('PUT','1234').content=='PUT 1234'
        assert client.request('PUT','1234/5678').content=='PUT 1234 5678'



    def test_app_xmethod(self):
                
        app = xio.app()
        @app.bind('www')
        def _(req): 
            """
            options: ABOUT,GET,POST,XMETHOD1,XMETHOD2
            """
            return req.xmethod or req.method

        ## direct call
        assert app.get('www').content=='GET' 
        assert app.post('www').content=='POST' 
        #assert app.delete('www').status==405
        #assert app.xmethod1('www').content=='XMETHOD1'
        #assert app.xmethod3('www').status==405

        ## chain call
        assert app.get('www').post().content=='POST'
        #assert app.get('www').xmethod1().content=='XMETHOD1'
        #assert app.get('www').xmethod3().status==405
        #assert app.get('www').delete().status==405

        ## request call
        assert app.request('GET','www').content=='GET'
        #assert app.request('XMETHOD1').content=='XMETHOD1'
        #assert app.request('XMETHOD3').status==405

        # client call
        cli = xio.resource( app )
        assert cli.get().content=='GET' 
        assert cli.post().content=='POST' 
        #assert cli.xmethod1().content=='XMETHOD1'
        

    def _test_app_www_content_type(self):
    
        from .apptest.app import app 

        # check index
        assert app.get('www').content.read().strip() == 'INDEX'
        assert app.get('www/index.html').content_type == 'text/html'
        assert app.get('www/static/test.json').content_type == 'application/json'



if __name__ == '__main__':

    unittest.main()












  





