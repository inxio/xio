#!/usr/bin/env python
#-*- coding: utf-8 -*--


import unittest

from xio.core.tests.common import checkPeer

import xio
import sys
from pprint import pprint



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
        user2 = xio.user(key=user1.key._private)
        assert user2.id==user1.id
        user3 = xio.user(token=user1.token)
        assert user3.id==user1.id

        print (user1.id)
        print (user2.id)
        print (user3.id)
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






