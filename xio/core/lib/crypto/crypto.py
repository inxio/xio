#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .common import *

import sys
import hashlib
import base64
import uuid
import json
import time

from .naclHandler import NaclHandler

try:
    # warning => segmentation fault if this import is in Key.account() !!!!!
    from xio.core.network.ext.ethereum.account import Account as ethereum_handler
except:
    ethereum_handler = None

def key(*args,**kwargs):
    return Key(*args,**kwargs)

class Key:

    def __init__(self,priv=None,token=None,seed=None):

        handler_cls = NaclHandler

        self._accounts = {}

        if token:
            
            self._handler = handler_cls # no instance, only static method allowed
            #self.ethereum = ethereum_handler
            self.private = None
            self.public = None
            self.token = token
            self.address = self.recoverToken(token)
            self.encryption = None
        else:        
            self._handler = handler_cls(private=priv,seed=seed)
            self.private = self._handler.private
            self.public = self._handler.public
            self.address = self.public #self._handler.address
            self.token = self.generateToken() if not token else token
            self.encryption = self._handler.encryption
            assert len(self.private)==64

        # fix id & token => utf8
        self.address = to_string(self.address)
        self.token = to_string(self.token)


    def account(self,network):
        if not network in self._accounts:
            account = ethereum_handler(seed=self.private) if ethereum_handler else None
            self._accounts[network] = account
        return self._accounts.get(network)
            


        
    def encrypt(self,message,*args,**kwargs):
        return self.encryption.encrypt(message,*args,**kwargs)

    def decrypt(self,message,*args,**kwargs):
        return self.encryption.decrypt(message,*args,**kwargs)

    def sign(self,message):
        return self._handler.sign(message)
        
    def verify(self,message,sig):
        return self._handler.verify(message,sig)

    def generateToken(self,scheme=None):
        h = self._handler if not scheme else self.account(scheme)
        return h.generateToken()


    def recoverToken(self,token,scheme=None):
        if isinstance(token,tuple):
            scheme,token = token
            scheme = scheme.split('/').pop()

        h = self._handler if not scheme else self.account(scheme)
        return h.recoverToken(token)


