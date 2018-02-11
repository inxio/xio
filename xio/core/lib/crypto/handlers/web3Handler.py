#!/usr/bin/env python
# -*- coding: utf-8 -*-


import web3.account
from .common import *


class Web3Handler:

    def __init__(self,private=None,seed=None):

        self._web3 = web3.Web3('')

        if private:
            self._account = self._web3.eth.account.privateKeyToAccount(private)
            self.private = private
            self.address = account.address
        elif seed:
            seed = sha3_keccak_256( seed )
            self._account = self._web3.eth.account.create(seed)
            self.private = self._account.privateKey.hex()[2:]
        else:
            self._account = self._web3.eth.account.create()
            self.private = self._account.privateKey.hex()[2:]
            
        self.address = self._account.address
        self.address = self._web3.toChecksumAddress(self.address) 

    
    def sign(self,message):
        sig = self._account.sign(message_text=message)
        v = sig.v
        r = sig.r.hex()
        s = sig.s.hex()
        return (v,r,s)

    def recover(self,message,sig): 
        (v,r,s) = sig
        address = self._web3.eth.account.recoverMessage(text=message,vrs=(v,r,s))
        return address
       

