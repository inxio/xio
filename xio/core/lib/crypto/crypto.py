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

        if token:
            self._handler = handler_cls # no instance, only static method allowed
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

        ethereum_handler = BITCOIN_ETH_HANDLER or WEB3_HANDLER
        self.ethereum = None
        if ethereum_handler:
            self.ethereum = ethereum_handler(seed=self.private)
            try: 
                self.ethereum.address = to_string(self.ethereum.address)
                self.ethereum.address = web3.Web3('').toChecksumAddress(self.address)  
            except:
                pass   

        
    def encrypt(self,message,*args,**kwargs):
        return self.encryption.encrypt(message,*args,**kwargs)

    def decrypt(self,message,*args,**kwargs):
        return self.encryption.decrypt(message,*args,**kwargs)

    def sign(self,message):
        return self._handler.sign(message)
        
    def verify(self,message,sig):
        return self._handler.verify(message,sig)

    def generateToken(self):
        nonce = str(int(time.time()))
        message = b'%s-%s' % (str_to_bytes(self.address),str_to_bytes(nonce))
        sig = self.sign(message)
        token = b'-'.join(sig)
        assert self.recoverToken(token)==self.address
        return token


    def recoverToken(self,token):
        token = str_to_bytes(token)
        nfo = token.split(b'-')
        verifikey = nfo[0]
        signed = nfo[1]
        message = self.verify(verifikey,signed)
        address,nonce = message.split(b'-')
        return address


