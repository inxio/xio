#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
from pprint import pprint
import sys

import xio



class TestCases(unittest.TestCase):

    def test_base(self):

        root = xio.resource()
        test1 = root.put('test1','OK1')
        test2 = root.put('test2','OK2')    
        test21 = test2.put('test21','OK21') 
        test3 = root.put('test3',lambda req: 'OK3')

        assert root.get('test1').content == 'OK1'
        assert root.get('test2').content == 'OK2'
        assert root.get('test2').get('test21').content == 'OK21'

        # check resources are the sames when using handler (prevent children lost, etc)
        assert test1 == root.get('test1') == root.get('test1')
        # warning each resource may difer in handler case
        #assert test3 == root.get('test3') == root.get('test3')


        root = xio.resource()
        root.put('www', lambda req: 'OK' if req.GET else req.PASS)
        root.put('www/page1', 'PAGE1' )
        assert root.get('www').content == 'OK'
        assert root.get('www/page1').content == 'PAGE1'
        

    def test_base_handler(self):

        root = xio.resource()
        root.put('www',lambda req: req._debug() )

        root = xio.resource( lambda req: req._debug() )
        assert root.get().content


    def test_base_client(self):
        root = xio.resource( lambda req: fail() if not req.GET else 'ok' )

        assert root.get().status == 200
        assert root.post().status == 500

        cli = xio.resource( root )
        assert cli.get().status == 200
        assert cli.post().status == 500


    def test_chain_without_handler(self):
        # gestion chain 

        root = xio.resource()
        c = root.put('a/b/c','OKc')
        d = c.put('d','OKd')
        e = root.put('a/b/e','OKe')
        h = root.get('a/b/c').put('f/g/h','OKh')
        k = root.get('a/b/c').put('i/j/k','OKk')
        #h = root.put('a/b/c').put('l/m/n','OKn') 

        assert root.get('a/b/c/d').content=='OKd'
        assert root.get('a/b').get('c').get('i').get('j/k')==root.get('a/b/c/i/j/k')
        assert root.get('a/b/c/i/j/k')


    def test_chain_with_handler(self):
        # gestion chain et handler 

        root = xio.resource()
        root.put('www', lambda req: "OK %s %s" % (req.method, req.path) )

        www = root.get('www')
        #assert callable( www.content ) # fail !
        assert www.get('').content == 'OK GET '
        assert www.put('mydata').content == 'OK PUT mydata'
        assert www.post('').content == 'OK POST '
        assert root.get('www/a').content=='OK GET a'
        assert root.get('www/a/b').content=='OK GET a/b'
        assert root.get('www/a/b/c').content=='OK GET a/b/c'

        assert root.get('www/a/b/c').content == root.get('www').get('a').get('b').get('c').content=='OK GET a/b/c'
        assert root.get('www').get('a').get('b').get('c').content == 'OK GET a/b/c' 
        assert root.get('www/a').get('b/c').content == root.get('www/a/b').get('c').content == root.get('www').get('a/b/c').content == 'OK GET a/b/c'

    def test_404(self):
        root = xio.resource()
        res1 = root.put('test1','OK1')
        res2 = root.put('test2/test3','OK2')     
        assert root.get('test1')==res1
        assert root.get('test2').get('test3')==res2

        # __nonzero__ compare le contenu de la resource
        assert root.get('a').status == 404
        #assert not root.get('a')
        #assert not root.get('a').get('a') 
        #assert root.get('a').get('a') != None

        assert root.get('test1').content == 'OK1'

        # same result using client
        cli = xio.resource( root )
        assert cli.get('a').status == 404


    def test_500(self):
        root = xio.resource()
        root.put('test1',lambda req: fail() if req.query else None)      

        # direct request  
        assert root.get('test1').status == 200
        assert root.get('test1',{'key':'val'}).status == 500

        # same result using client
        cli = xio.resource( root )
        assert root.get('test1',{'key':'val'}).status == 500


    def test_routes(self):
        
        root = xio.resource()
        root.put(':a','a')
        root.put(':a/:b','a/b')
        root.put(':a/:b/:c','a/b/c')

        assert root.get('1').content == 'a'
        assert root.get('1/2').content == 'a/b'
        assert root.get('1/2/3').content == 'a/b/c'

        root = xio.resource()
        root.put(':a',lambda req: 'a' if req.GET else req.PASS)
        root.put(':a/:b',lambda req: 'a/b' if req.GET else req.PASS)
        root.put(':a/:b/:c',lambda req: 'a/b/c' if req.GET else req.PASS)

        assert root.get('1',{}).content == 'a'
        assert root.get('1/2',{}).content == 'a/b'
        assert root.get('1/2/3',{}).content == 'a/b/c'


    def test_routes_handler(self):

        root = xio.resource()
        root.bind('a', lambda req: 'a handler')
        root.bind('a/:b', lambda req: 'b handler')
        root.bind('a/:b/:c',lambda req: 'c handler')

        assert root.get('a').content=='a handler'
        assert root.get('a/b').content=='b handler'
        assert root.get('a/b/c').content=='c handler'

        assert root.post('a').content=='a handler'
        assert root.post('a/b').content=='b handler'
        assert root.post('a/b/c').content=='c handler'

        assert root.put('a').content=='a handler'
        assert root.put('a/b').content=='b handler'
        assert root.put('a/b/c').content=='c handler'



    def test_routes_params(self):

        root = xio.resource()
        root.put('www/:container', lambda req: req.context if req.GET else req.PASS  )
        root.put('www/:container/:item', lambda req: req.context )

        c = root.get('www/:container')
        c1 = root.get('www/container1')
        c2 = root.get('www/container2')
        assert c1._handler == c1._handler == c._handler

        data = root.get('www/container1/1234',{'var1':'ok'}).content
        assert data[':container'] == 'container1'
        assert data[':item'] == '1234'



    def test_about_inline(self):

        root = xio.resource()

        @root.bind('test1')
        def _(req):
            """
            options: GET,POST
            input:
                params:
                    - name: param1
                    - name: param2
            """
            if req.GET or req.POST:
                return 'ok1'

        @root.bind('test2')
        def _(req):
            """
            options: MYCUSTOMMETHOD
            input:
                params:
                    - name: myparam
            """
            if req.MYCUSTOMMETHOD:    
                return 'ok2'

        @root.bind('test3')
        def _(req):
            """
            options: GET,POST
            description: 2x multiplication
            input:
                params:
                    -   name: param1
                        required: true    
            tests:
                -   method: GET
                    input:
                        param1: 12
                    assert: 
                        content: 24
                -   method: POST
                    input:
                        param1: 25
                    assert: 
                        content: 25
          
            """
            return 2*int( req.input.get('param1') ) 

        about = root.about('test1').content
        assert about != 'ok1'
        assert 'POST' in about['options']
        assert 'param2' in str(about['methods']['POST']['input']['params'])

        about = root.about('test2').content
        assert 'MYCUSTOMMETHOD' in about['options']
        assert 'myparam' in str(about['methods']['MYCUSTOMMETHOD']['input']['params'])
        assert root.get('test2').mycustommethod('myvalue').content == 'ok2'

        testresult = root.get('test3',{'param1':300})
        assert testresult.status == 200
        assert testresult.content == 600




    def test_xmethod(self):

        root = xio.resource()

        @root.bind('www')
        def _(req):
            """
            options: CUSTOMMETHOD1, CUSTOMMETHOD2
            """
            return 'OK %s %s' % (req.method, req.xmethod)

        www = root.get('www')
        # declared methods
        assert www.customMethod1().content == 'OK POST CUSTOMMETHOD1'
        assert www.customMethod2().content == 'OK POST CUSTOMMETHOD2'
        # undeclared methods
        assert www.customMethod3().status == 405 # method not allowed



    def test_handler_checkpoint(self):
        
        root = xio.resource()

        @root.bind('www')
        def _(req):
            """
            options: GET, POST
            input:
                params:
                    -   name: param1
                        required: true
                    -   name: param2
                        required: true
                        type: integer
                    -   name: param3
                        type: float
                    -   name: param4
                        pattern: 'OK(.*)OK'
            """
            return 'TESTOK'

        www = root.get('www')

        # declared methods
        assert www.get().status == 400                                              # missing args param1
        assert www.get({'param1':'value1'}).status == 400                           # missing args param2
        assert www.get({'param1':'value1','param2':'value2'}).status == 400         # param2 must be integer
        assert www.get({'param1':'value1','param2':123}).status == 200              # ok
        assert www.get({'param1':'value1','param2':123,'param3':'value2'}).status == 400        # param3 must be float
        assert www.get({'param1':'value1','param2':123,'param3':5.5}).status == 200             # ok
        assert www.get({'param1':'value1','param2':123,'param4': 'test'}).status == 400         # pattern not match
        assert www.get({'param1':'value1','param2':123,'param4': 'OKtestOK'}).status == 200     # ok
        assert www.delete().status == 405   # method not allowed

                


    def test_prevent_path_modifications(self):
        """
        check that any path update by handlers won't impact parent resource path 
        handlers need to use req.redirect for any path redirection for requestt handling
        """

        root = xio.resource()
        @root.bind('test')
        def _(req):
            req.path = 'some updated path by handler'
            return 'ok'

        test1 = root.get('test')
        test2 = test1.get()

        assert test1.content == test2.content == 'ok'
        assert test1.path == test2.path == 'test'



    def test_api(self):

        root = xio.resource()
        @root.bind('www/test1')
        def _(req):
            """
            options: GET,POST
            input:
                params:
                    - name: param1
                    - name: param2
            """
            if req.GET or req.POST:
                return 'ok1'

        @root.bind('www/test2')
        def _(req):
            """
            options: MYCUSTOMMETHOD
            input:
                params:
                    - name: myparam
            """
            if req.MYCUSTOMMETHOD:    
                return 'ok2'

        about = root.about().content
        assert about.get('resources',{}).get('www')!=None

        about = root.get('www').about().content

        assert 'test1' in about.get('resources')
        assert 'test2' in about.get('resources')

        api = root.api().content
        assert api
        



    def test_handler_instance(self):

        instance = xio.app()
        cli = xio.resource( instance )
        assert cli.about().content['id']==instance.id

    def test_handler_http(self):
        cli = xio.resource( 'http://127.0.0.1' )


    def _test_handler_namespace(self):
        xio.handlers.bind('myns', lambda req: 'namespace %s ok' % req.path)
        cli = xio.resource('myns:somepath')
        assert cli.get('subpath').content=='namespace somepath/subpath ok' 
        assert cli.get().content=='namespace somepath ok' ####################### tofix namespace somepath/ ok

    def _test_handler_xrn(self):
        root = xio.resource('xrn:test')
        assert root._handler

    def test_handler_directory(self):
        # file://host/path or file:///path
        directory = os.path.dirname( os.path.realpath(__file__) )
        client = xio.resource('file://'+directory)
        assert client._handler

        resp = client.get()
        assert resp.status == 200
        assert resp.content

    def test_handler_file(self):

        filepath = os.path.realpath(__file__)
        client = xio.resource('file://'+filepath)
        
        resp = client.get()
        assert resp.status == 200
        assert resp.content

        
    def test_handler_http(self):

        root = xio.resource('http://127.0.0.1')
        assert root._handler

        root = xio.resource('https://127.0.0.1/subpath')
        assert root._handler

        """
        client = xio.resource('http://127.0.0.1')
    
        resp = client.get('/')


        assert resp.status == 200

        root = client.head()
        assert root.status == 200
        assert not root.content
        """
        """
        lib = root.get('lib')
        assert lib.status == 200
        assert lib.content 
        """



    def test_handler_callable(self):
        root = xio.resource( lambda req: req.path )
        assert root._handler

    def test_handler_resource(self):
        app = xio.app()
        root = xio.resource( app )
        assert root._handler



                
if __name__ == '__main__':

    unittest.main()












  





