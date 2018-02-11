#!/usr/bin/env python
#-*- coding: utf-8 -*--


import unittest

import xio
import sys
from pprint import pprint



def checkPeer(peertype):

    factory = getattr(xio,peertype)
    assert factory

    assert factory().id != factory().id, Exception('ERROR GENETERATE UID %s' % peertype)

    # server instance    
    seed = u'myseed%s' % peertype
    assert factory(seed=seed).id == factory(seed=seed).id
    peer = factory()
    assert peer.id
    assert peer.uuid
    assert peer.token
    assert peer.key
    assert peer.key.private
    assert peer.key.public
    assert peer.key.address


    # basic client instance 
    cli1 = xio.client(peer)
    # client instance using server instance .. eg xio.app( app )
    from xio.core import resource
    cli2 = factory(peer)
    # client instance using id/xrn
    cli3 = factory(peer.id)

    for cli in [cli1,cli2,cli3]:
        assert cli and cli.__class__.__name__.lower()=='resource', Exception('ERROR FACTORY %s' % peertype)
        #assert cli.about().content and cli.about().content.get('id')==peer.id, Exception('ERROR FACTORY %s' % peertype) #### totfix: pb user
     

    # peer about
    assert peer.about().content.get('id')==peer.id
    assert peer.about().content.get('type')==peertype
    cli = xio.resource(peer)
    assert cli.about().content.get('id')==peer.id
    assert cli.about().content.get('type')==peertype

    # peer connection
    user = xio.user()
    cli = user.connect(peer)
    assert cli.context.get('client').id == user.id

    app = xio.app(seed='myapp')
    app.put('www',lambda req: req._debug() )
    cli = peer.connect(app)
    info = cli.get().content
    assert info.get('client').get('id')==peer.id

    # peer peers
    assert peer.peers
    peer.peers.register(app)
    assert peer.peers.db.count()==1

    # peer network
    assert peer.network



class TestCases(unittest.TestCase):


    def test_peers_base(self):

        user = xio.user()
        cli = xio.client( user )
        assert cli.about().content.get('id')==user.id
        pprint(cli.about().content)

        app = xio.app()
        cli = xio.client( app )
        pprint(cli.about().content)
        assert cli.about().content.get('id')==app.id



    def test_base(self):

        for peertype in ['user','app','node','network']:
            checkPeer(peertype)   


    def test_connect(self):

        user = xio.user()
        app = xio.app()
        node = xio.node()
        network = xio.network()
        
        # user->app
        cli = user.connect(app)
        assert cli.about().content.get('id')==app.id

        # app->user
        cli = app.connect(user)
        assert cli.about().content.get('id')==user.id        

        # app->node
        cli = app.connect(node)
        assert cli.about().content.get('id')==node.id   

        # node->app
        cli = node.connect(app)
        assert cli.about().content.get('id')==app.id 

        # node->network
        cli = node.connect(network)
        assert cli.about().content.get('id')==network.id 


    def test_recover(self):
    
        user1 = xio.user()
        user2 = xio.user(key=user1.key.private)
        assert user2.id==user1.id
        user3 = xio.user(token=user1.token)
        assert user3.id==user1.id
        assert user1.id==user2.id==user3.id


    def test_crypt(self):
    
        message = b'some data'
        user = xio.user()
        crypted = user.encrypt(message) 
        assert crypted
        decrypted = user.decrypt(crypted) 
        assert message==decrypted
 


if __name__ == '__main__':

    unittest.main()






