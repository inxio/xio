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



    def _test_base(self):

        for peertype in ['user','app','node','network']:
            checkPeer(peertype)   


    def test_base2(self):
       
        # check that network peer address is contract address
        assert network.id 
        assert root.getBalance()>0
        assert seller.getBalance()>0

        services = network.getServices()
        import collections
        assert isinstance(services, collections.Iterable) # list or generator


    """

    def test_peers_base2(self):

        app = xio.app()
        cli = xio.app( app )
        pprint(cli.about().content)
        assert cli.about().content.get('id')==app.id


        user = xio.user()
        cli = xio.user( user )
        assert cli.about().content.get('id')==user.id
        pprint(cli.about().content)

        service = xio.service()
        cli = xio.user( service )
        assert cli.about().content.get('id')==service.id


    def _test_peers2(self):
        
        for peertype in ['user','app','node']: #,'service','network'
            checkPeer(peertype)    
            


    def test_connect(self):

        user = xio.user()
        app = xio.app()
        node = xio.node()

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


    def test_p2p_old(self):
        # connection app->node (old style)
        node = xio.node()
        user = xio.user()
        cli = xio.app( node ) # pb car app client donc pas de id
        res = cli.get('user')
        print('??',res.status) ######## bug
        #assert res.status==401
        print('??',res.content) ######## bug
        cli.xio_token = user.token
        #print cli.xio_token
        print ( cli.get('user') )


    def test_p2p(self):
        # onnect peux gerer tout en fait et c'est plus clair que user1.client(user2) et permet des conenction customisable. :  app.connect('xrn:inxio:ftp', {**profile} )

        node = xio.node()
        app1 = xio.app()
        app2 = xio.app()
        user1 = xio.user()
        user2 = xio.user()
        assert app1.id != app2.id and user1.id !=user2.id

        user1.connect(node)
        user2.connect(node)
        app1.connect(node)
        app2.connect(node)



    def test_peer_send_value(self):

        root = xio.user(seed='root') # prevent network change
    
        user1 = xio.user()
        assert user1.getBalance()==0

        user2 = root
        assert user2.getBalance()>0

        # send value user=>user
        user2.send(user1, 120)
        assert user1.getBalance()==120

        # send value user=>app
        app = xio.app()
        assert app.getBalance()==0
        user2.send(app, 150)
        assert app.getBalance()==150

        # check rawTransactions
        user1 = xio.user()
        root.send(user1, 200)
        assert user1.getBalance()==200

        user2 = xio.user()
        user1.send(user2,100)
        assert user2.getBalance()==100



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
 
    """

if __name__ == '__main__':

    unittest.main()






