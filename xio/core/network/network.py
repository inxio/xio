#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xio.core import peer 


def network(*args,**kwargs):
    return Network.factory(*args,**kwargs)


class Network(peer.Peer):

    def __init__(self,**kwargs):
        peer.Peer.__init__(self,**kwargs) 




