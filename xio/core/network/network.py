#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xio.core import peer 
from xio.core.peers import Peers
from xio.core.lib.utils import is_string, urlparse
from xio.core.lib.logs import log

def network(*args,**kwargs):
    return Network.factory(*args,**kwargs)


class Network(peer.Peer):

    peers = None

    def __init__(self,id=None,**kwargs):
        
        peer.Peer.__init__(self,**kwargs) 
        self.peers = Peers()
        self.network = self
        self.log = log


    @classmethod
    def factory(cls,id=None,*args,**kwargs):

        if id and is_string(id) and id.startswith('0x'):
            from networkHandler import NetworkHandler
            id = NetworkHandler(id)

        # check networkhandler
        if id and callable(id):
            network = Network(handler=id)
            return network

        if not id:
            return cls(**kwargs)
                
        return peer.Peer.factory(id,*args,_cls=cls,**kwargs)


