#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xio.core import peer 

def user(*args,**kwargs):
    return User.factory(*args,**kwargs)


class User(peer.Peer):

    def __init__(self,**kwargs):
        peer.Peer.__init__(self,**kwargs) 

