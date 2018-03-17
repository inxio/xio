#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import xio
import sys
from pprint import pprint


"""
app = xio.app()
node = xio.node()
node.register( app )
print node.about('www/'+app.id).content

cli = xio.client(node)
print cli.about(app.id).content
sys.exit()
"""

class TestCases(unittest.TestCase):


    def test_base_server(self):

        node = xio.node()
        node.register( xio.app() )
        node.register( xio.user() )
        assert node.peers.db.count()==2

       
    def test_base_client(self):

        app1 = xio.app()
        app2 = xio.app()

        node = xio.node()
        node.register( app1 )
        node.register( app2 )

        cli = xio.client(node)
        assert len( cli.get().content ) == 2
        assert cli.about(app1.id).content.get('id')==app1.id
        assert cli.about(app2.id).content.get('id')==app2.id
        assert cli.get(app1.id).about().content.get('id')==app1.id
        assert cli.get(app2.id).about().content.get('id')==app2.id


    def test_node_connect(self):

        node = xio.node()

        app = xio.app()
        app.put('www',lambda req: req._debug() if req.GET else req.PASS )
        node.register(app)
        
        user = xio.user()
        cli = user.connect(node)
        assert cli.about(app.id).content.get('id')==app.id
        assert cli.get(app.id).content.get('client').get('id')==user.id



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



    def test_node_delivery(self):

        node = xio.node()
        app = xio.app()
        app.put('www',lambda req: req._debug() if req.GET else req.PASS )
        peer = node.peers.register(app)
        cli = xio.client(node)

        # deliver by id
        res = node.request('ABOUT','www/'+app.id)
        assert res.status ==  200
        assert res.content.get('id') == app.id
        assert cli.about(app.id).content.get('id') == app.id
        
        # deliver by uid
        res = node.request('ABOUT','www/'+peer.uid)
        assert res.status ==  200
        assert res.content.get('id') == app.id
        assert cli.about(peer.uid).content.get('id') == app.id

        # request handling
        assert cli.get(app.id).content.get('method') == 'GET'
        


    def test_base_sync(self):

        node1 = xio.node()
        node2 = xio.node()
    
        # register app on node1
        node1.register( xio.app() )
        # register node1 on node2
        node2.peers.register(node1)
        # sync node2
        node2.peers.sync()
        
        assert node2.peers.db.count()==2


      
    """  




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



    def _test_network_sync(self):

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

            
    """



if __name__ == '__main__':

    unittest.main()












  





