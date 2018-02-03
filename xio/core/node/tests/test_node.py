#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import xio
import sys
from pprint import pprint

#from xio.network.tests import common





class TestCases(unittest.TestCase):

    def setUp(self):
        # init new network
        #xio.context.network = xio.network()
        pass

    def test_base_server(self):

        common.checkPeer('node')

        node = xio.node()
        node.register( xio.app() )
        node.register( xio.user() )

        assert node.network
        assert node.peers
        assert node.peers.db.count()==2
        assert len( node.peers.select(type='app') )==1
        assert len( node.peers.select(type='user') )==1
        

    def test_base_client(self):

        app1 = xio.app()
        app2 = xio.app()

        node = xio.node()
        node.register( app1 )
        node.register( app2 )

        cli = xio.resource(node)
        assert len( cli.get().content ) == 2
        assert cli.about(app1.id).content.get('id')==app1.id
        assert cli.about(app2.id).content.get('id')==app2.id
        assert cli.get(app1.id).about().content.get('id')==app1.id
        assert cli.get(app2.id).about().content.get('id')==app2.id



    def test_node_register(self):
        
        node = xio.node()
        assert node.peers.db.count()==0
        node.register( xio.app() )
        node.register( xio.user() )
        node.register( xio.service() )
        node.register( xio.asset() )
        node.register( xio.node() )
        node.register( xio.network() )
        assert node.peers.db.count()==6

    def test_node_connect(self):

        node = xio.node()

        app = xio.app()
        app.put('www',lambda req: req._debug() if req.GET else req.PASS )
        node.register(app)
        
        user = xio.user()
        cli = user.connect(node)
        assert cli.about(app.id).content.get('id')==app.id
        assert cli.get(app.id).content.get('client').get('id')==user.id



    def test_export(self):

        app1 = xio.app()
        app2 = xio.app()

        node = xio.node()
        node.register( app1 )
        node.register( app2 )

        # check db
        assert node.peers.db.count()==2

        # check export
        export = node.peers.export()
        assert len(export)==2



    def test_base_sync(self):

        # base test
        node1 = xio.node()
        node1.peers.register( xio.app() )

        # node1 => node2
        node2 = xio.node()
        assert node2.peers.db.count()==0
        node2.peers.register(node1)
        assert node2.peers.db.count()==1
        node2.peers.sync()
        assert node2.peers.db.count()==2

        # node2 => node1
        node2.peers.register( xio.app() )
        node1.peers.register(node2)
        node1.peers.sync()
        assert node1.peers.db.count()>=3

        # biderectionnel sync

        app1 = xio.app()
        node1 = xio.node()

        app2 = xio.app()
        node2 = xio.node()

        node1.peers.register(app1)
        node1.peers.register(node2)
        assert node1.peers.get(app1.id).id == app1.id
        assert node1.peers.get(node2.id).id == node2.id

        node2.peers.register(app2)
        node2.peers.register(node1)
        assert node2.peers.get(app2.id).id == app2.id
        assert node2.peers.get(node1.id).id == node1.id


        # before sync
        assert not node2.peers.get(app1)
        assert not node2.peers.get(app1)

        # check export
        export = node1.peers.export()
        assert len(export)==2

        # syncing
        node1.peers.sync()
        node2.peers.sync()

        # check export
        export = node1.peers.export()
        assert len(export)>=3

        
        

    def test_register2(self):

        node = xio.node()

        app = xio.app()
        peer = node.peers.register(app)
        assert peer.id == app.id
        assert node.peers.get(peer.uid).id == app.id
        assert node.peers.get(app.id).id == app.id
        assert node.peers.select(id=app.id)[0].id == app.id

        user = xio.user()
        peer = node.peers.register(user)
        assert peer.id == user.id
        assert node.peers.get(peer.uid).id == user.id
        assert node.peers.get(user.id).id == user.id
        assert node.peers.select(id=user.id)[0].id == user.id

        node2 = xio.node()
        peer = node.peers.register(node2)
        assert peer.id == node2.id
        assert node.peers.get(peer.uid).id == node2.id
        assert node.peers.get(node2.id).id == node2.id
        assert node.peers.select(id=node2.id)[0].id == node2.id
        

    def test_node_unregister(self):

        node = xio.node()
        app = xio.app()

        peer = node.peers.register(app)
        assert node.peers.get(peer.uid).id == app.id

        node.peers.unregister(app.id)
        assert not node.peers.get(peer.uid)
        


    def test_node_lookup(self):

        node = xio.node()
        app = xio.app()
        peer = node.peers.register(app)

        # list all peers
        for peer in node.peers.select():
            assert peer.endpoint == app
            assert peer.id==app.id

        # get peer by uid
        assert node.peers.get( peer.uid ).id==app.id

        # get peer by id
        assert node.peers.select( id=peer.id )[0].id==app.id

        # get peer by nodeid
        #assert node.peers.select( nodeid=node.id )[0].id==app.id



    def test_peer_check(self):

        node = xio.node()
        app = xio.app()
        peer = node.peers.register(app)

        check = peer.check()
        assert check['status'] == 200
        #assert check['time'] > 0


    def test_peer_request(self):

        node = xio.node()
        app = xio.app()
        peer = node.peers.register(app)

        resp = peer.request('ABOUT','')
        assert resp.status==200
        assert resp.content.get('id')==app.id




    def test_node_delivery(self):

        node = xio.node()
        app = xio.app()
        peer = node.peers.register(app)

        # about
        res = node.request('ABOUT','www/'+app.id)
        assert res.status ==  200
        assert res.content.get('id') == app.id

        # deliver by id
        res = node.request('GET','www/'+app.id)
        assert res.status ==  200

        # deliver by uid
        res = node.request('GET','www/'+peer.uid)
        assert res.status ==  200

        # deliver by xrn
        #res = node.request('GET','www/xrn:xio:app1')
        #assert res.content ==  'OKAPP1'



    def _test_node_about_app(self):

        # check relative path for node resources
        app = xio.app()
        node = xio.node()
        node.peers.register(app)

        cli = node.request('GET','www/'+app.id) 
        assert cli.request('ABOUT','').content.get('id')==app.id
        assert cli.about().content.get('id')==app.id

        # check about retreiving
        app1 = xio.app()
        app1._about = {'name':'xrn:xio:app1'}
        app1.put('www', lambda req: 'OKAPP1') 

        node = xio.node()
        node.peers.register(app1) #######TOFIX

        app = node.request('GET','www/'+app1.id) 
        assert app.path == 'www/'+app1.id

        www1 = node.request('GET','www/'+app1.id).content 
        www2 = app.request('GET','').content 
        www3 = app.get().content 

        assert www1 == www2 == www3 == 'OKAPP1'

        about1 = node.request('ABOUT','www/'+app1.id).content 
        about2 = app.request('ABOUT').content 
        about3 = app.about().content

        assert about1 == about2 #== about3 


    def test_network(self):

        xio.context.network = None

        node1 = xio.node()
        node2 = xio.node()

        node1.peers.register(node2)
        node2.peers.register(node1)

        for peer in node1.peers.select():
            assert peer.type == 'node'
            assert peer.id == node2.id

        for peer in node1.peers.select():
            assert peer.type == 'node'
            assert peer.id == node2.id


    def test_network_sync(self):

        #xio.context.network = None

        app1 = xio.app()
        app2 = xio.app()

        node1 = xio.node()
        node1.peers.register(app1)
        node1.peers.register(app2)

        node2 = xio.node()
        node2.peers.register(node1)

        node3 = xio.node()
        node3.peers.register(node2)

        assert not node2.peers.get(app1)
        assert not node2.peers.get(app2)

        node2.peers.sync()

        assert node2.peers.get(app1)
        assert node2.peers.get(app2)

        node3.peers.sync()

        assert node3.peers.get(app1)
        assert node3.peers.get(app2)

        assert node2.about(app1).content.get('id')==app1.id
        assert node3.about(app1).content.get('id')==app1.id



    def _test_network_sync_loop(self):

        node1 = xio.node()

        node1.peers.register(node1) 

        assert not node1.peers.register(node1)

        node1 = xio.node()
        node2 = xio.node()
        node3 = xio.node()

        node1.peers.register(app1)
        node1.peers.register(node1)
        node1.peers.register(node2)
        node1.peers.register(node3)

        node2.peers.register(app2)
        node2.peers.register(node1)
        node2.peers.register(node2)
        node2.peers.register(node3)

        node3.peers.register(node1)
        node3.peers.register(node2)

        for i in range(0,10):
            node1.peers.sync()
            node2.peers.sync()
            node3.peers.sync()
            
        nbpeers = len( list(node3.peers.getNodes()) )
        nbapp1 = len( list(node3.peers.getApps('ID01')) )

        assert nbpeers==2
        assert nbapp1==2

            




if __name__ == '__main__':

    unittest.main()












  





