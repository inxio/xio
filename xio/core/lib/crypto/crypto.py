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
    from .handlers.bitcoinHandler import BitcoinHandler, BitcoinEthereumHandler
    BITCOIN_ETH_HANDLER = BitcoinEthereumHandler
    BITCOIN_HANDLER = BitcoinHandler
except Exception as err:
    BITCOIN_ETH_HANDLER = None
    BITCOIN_HANDLER = None

try:
    from .handlers.web3Handler import Web3Handler
    WEB3_HANDLER = Web3Handler
except Exception as err:
    WEB3_HANDLER = None




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

        ethereum_handler = BITCOIN_ETH_HANDLER or WEB3_HANDLER
        if ethereum_handler:
            self.ethereum = ethereum_handler(seed=self.private)
        """
        try: 
            self.ethereum.address = web3.Web3('').toChecksumAddress(self.address)  
        except:
            self.ethereum = None    
        """
        
    def encrypt(self,message,*args,**kwargs):
        return self.encryption.encrypt(message,*args,**kwargs)

    def decrypt(self,message,*args,**kwargs):
        return self.encryption.decrypt(message,*args,**kwargs)

    def sign(self,message):
        return self._handler.sign(message)
        
    def verify(self,message,sig):
        return self._handler.verify(message,sig)
        
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


    def generateToken(self):
        nonce = str(int(time.time()))
        message = b'%s-%s' % (str_to_bytes(self.address),str_to_bytes(nonce))
        sig = self.sign(message)
        token = b'-'.join(sig)
        assert self.recoverToken(token)==self.address
        
        return token

        """
        token = nonce+b'-'+b'-'.join([str_to_bytes(p) for p in sig])
        if hasattr(self._handler,'recover'):
            address = nonce or str(int(time.time()))  # warning : wrong address recovered if int   
            sig = self.sign(nonce)
            if isinstance(sig,tuple):
                # web3, nacl
                token = nonce+'-'+'-'.join([str(p) for p in sig])
            else:
                # other
                token = nonce+'-'+sig
        else:
            base = self.address+'-'+nonce
            sig = self.sign(base)
            sig = encode_hex(sig)
            token = base+'-'+sig

        # check
        address = self.recoverToken(token)
        assert address==self.address
        return token
        """

    def recoverToken(self,token):
        nfo = token.split(b'-')
        verifikey = nfo[0]
        signed = nfo[1]
        message = self.verify(verifikey,signed)
        address,nonce = message.split(b'-')
        return address

        """
        nfo = token.split('-')
        if len(nfo)==3:
            address = nfo[0]
            nonce = nfo[1]
            sig = nfo[1]
            
            assert self.verify(address+'-'+nonce,sig)
            
        else:
            # OLD VERSION
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
        """

