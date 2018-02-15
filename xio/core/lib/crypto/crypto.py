#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .handlers.common import *

import sys
import hashlib
import base64
import uuid
import json
import time

from .handlers.naclHandler import NaclHandler


try:
    from .handlers.web3Handler import Web3Handler
    WEB3_HANDLER = Web3Handler
except Exception as err:
    WEB3_HANDLER = None


try:
    from .handlers.bitcoinHandler import BitcoinHandler, BitcoinEthereumHandler
    BITCOIN_ETH_HANDLER = BitcoinEthereumHandler
    BITCOIN_HANDLER = BitcoinHandler
except Exception as err:
    BITCOIN_ETH_HANDLER = None
    BITCOIN_HANDLER = None



def key(*args,**kwargs):
    return Key(*args,**kwargs)

class Key:

    def __init__(self,priv=None,token=None,seed=None):

        handler_cls = NaclHandler
        ethereum_handler = BITCOIN_ETH_HANDLER or WEB3_HANDLER

        if token:
            self._handler = handler_cls # no instance, only static method allowed
            self.ethereum = ethereum_handler
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

            self.ethereum = None
            if ethereum_handler:
                self.ethereum = ethereum_handler(seed=self.private)
                try: 
                    self.ethereum.address = to_string(self.ethereum.address)
                    self.ethereum.address = web3.Web3('').toChecksumAddress(self.address)  
                except:
                    pass   


        # fix id & token => utf8
        self.address = to_string(self.address)
        self.token = to_string(self.token)

        


        
    def encrypt(self,message,*args,**kwargs):
        return self.encryption.encrypt(message,*args,**kwargs)

    def decrypt(self,message,*args,**kwargs):
        return self.encryption.decrypt(message,*args,**kwargs)

    def sign(self,message):
        return self._handler.sign(message)
        
    def verify(self,message,sig):
        return self._handler.verify(message,sig)

    def generateToken(self,scheme=None):
        h = self._handler if not scheme else getattr(self,scheme)
        return h.generateToken()


    def recoverToken(self,token,scheme=None):
        if isinstance(token,tuple):
            scheme,token = token
            scheme = scheme.split('/').pop()
        h = self._handler if not scheme else getattr(self,scheme)
        return h.recoverToken(token)


