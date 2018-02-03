#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .handlers.common import *

import sys
import hashlib
import base64
import uuid
import json
import time
            
from .handlers.bitcoinHandler import BitcoinHandler

try:
    from .handlers.bitcoinHandler import BitcoinHandler
    BITCOIN_HANDLER = BitcoinHandler
except Exception as err:
    BITCOIN_HANDLER = None

try:
    from .handlers.web3Handler import Web3Handler
    WEB3_HANDLER = Web3Handler
except Exception as err:
    WEB3_HANDLER = None


try:
    from .handlers.naclHandler import NaclHandler
    NACL_HANDLER = NaclHandler
except:
    NACL_HANDLER = False



def key(*args,**kwargs):
    return Key(*args,**kwargs)

class Key:

    def __init__(self,priv=None,token=None,seed=None):

        handler_cls = BITCOIN_HANDLER or WEB3_HANDLER

        if token:
            self._handler = handler_cls # no instance, only static method allowed
            self._private = None
            self.public = None
            self.token = token
            self.address = self.recoverToken(token)
            self.encryption = None
        else:        
            self._handler = handler_cls(private=priv,seed=seed)
            self._private = self._handler.priv
            self.public = self._handler.pub
            self.address = self._handler.address
            self.token = self.generateToken() if not token else token

        try: 
            self.address = web3.Web3('').toChecksumAddress(self.address)  
        except:
            pass     
        
        self.encryption = NACL_HANDLER(self._private) if NACL_HANDLER and self._private else None


    def encrypt(self,message,*args,**kwargs):
        return self.encryption.encrypt(message,*args,**kwargs)

    def decrypt(self,message,*args,**kwargs):
        return self.encryption.decrypt(message,*args,**kwargs)

    def sign(self,message):
        return self._handler.sign(message)

    def export(self,password):
        import os
        import os.path
        import json
        assert self.key
        hname = self._w3.sha3(text=username).hex()
        filename = 'xio.user.'+hname
        crypted = self._w3account.encrypt(password)

        keystoredir = '/data/xio/keystore'
        if not os.path.isdir(keystoredir):
            os.makedirs(keystoredir)

        with open(keystoredir+'/'+filename,'w') as f:
            json.dump(crypted, f, indent=4)  


    def generateToken(self,nonce=None):
        if hasattr(self._handler,'recover'):
            nonce = nonce or str(int(time.time()))  # warning : wrong address recovered if int   
            sig = self.sign(nonce)
            if isinstance(sig,tuple):
                token = nonce+'-'+'-'.join([str(p) for p in sig])
            else:
                token = nonce+'-'+sig
        else:
            sig = self.sign(pub)
            sig = encode_hex(sig)
            token = pub+'-'+sig

        # check
        address = self.recoverToken(token)
        assert address==self.address
        return token


    def recoverToken(self,token):
        nfo = token.split('-')
        nonce = nfo.pop(0)
        sig = nfo
        if len(sig)==1: 
            if len(nonce)==128: #tofix  
                #ecda
                pub = nonce
                sig = sig[0]
                address = self._handler.verify(pub,pub,sig)
            else:   
                #bitcoin like
                sig = sig[0]
                address = self._handler.recover(nonce,sig)
        else: # ethereum
            address = self._handler.recover(nonce,sig)
        return address


