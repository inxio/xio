#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import xio
import sys
from pprint import pprint

from xio.core.peers import Peers


class TestCases(unittest.TestCase):


    def test_base(self):
    
        peers = Peers()
        assert peers.db.count()==0
                
        peers.register( xio.app() )
        peers.register( xio.user() )
        assert peers.db.count()==2
        assert len( peers.select(type='app') )==1
        assert len( peers.select(type='user') )==1

        peers.register( xio.app() )
        peers.register( xio.user() )
        peers.register( xio.node() )
        peers.register( xio.network() )
        assert peers.db.count()==6
        assert len( peers.select(type='app') )==2
        assert len( peers.select(type='user') )==2



    def test_export(self):

        peers = Peers()
        app1 = xio.app()
        app2 = xio.app()

        peers.register( app1 )
        peers.register( app2 )

        # check db
        assert peers.db.count()==2

        # check export
        export = peers.export()
        assert len(export)==2


    def test_peer_client(self):

        app = xio.app()
        
        peers = Peers()
        peers.register( app )
        
        peer = peers.get(app.id)
        assert peer
        assert peer.request('ABOUT').content.get('id')==app.id
        assert peer.about().content.get('id')==app.id

        
    def test_unregister(self):

        peers = Peers()
        app = xio.app()

        peer = peers.register(app)
        assert peers.get(peer.uid).id == app.id

        peers.unregister(app.id)
        assert not peers.get(peer.uid)



    def test_lookup(self):

        peers = Peers()
        app = xio.app()
        peer = peers.register(app)

        # list all peers
        for peer in peers.select():
            assert peer.endpoint == app
            assert peer.id==app.id

        # get peer by uid
        assert peers.get( peer.uid ).id==app.id

        # get peer by id
        assert peers.select( id=peer.id )[0].id==app.id


    def test_peer_check(self):

        peers = Peers()
        app = xio.app()
        peer = peers.register(app)

        check = peer.check()
        assert check['status'] == 200
        #assert check['time'] > 0



            




if __name__ == '__main__':

    unittest.main()












  





