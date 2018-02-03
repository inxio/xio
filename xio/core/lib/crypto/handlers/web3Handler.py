#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web3.account

class Web3Handler:

    @staticmethod
    def generateKeyPair(seed=None):
        account = web3.Web3('').eth.account.create()   
        key = account.privateKey.hex()[2:]
        address = account.address
        return (key,address)

    @staticmethod
    def priv2address(key):
        account = web3.Web3('').eth.account.privateKeyToAccount(key)
        key = account.privateKey.hex()[2:]
        address = account.address
        return address

    @staticmethod
    def sign(message,key):
        account = web3.Web3('').eth.account.privateKeyToAccount(key)
        sig = account.sign(message_text=message)
        v = sig.v
        r = sig.r.hex()
        s = sig.s.hex()
        return (v,r,s)

    @staticmethod
    def recover(message,sig): 
        # https://lab-blog.ey.com/2016/12/19/ecrecover/
        (v,r,s) = sig
        address = web3.Web3('').eth.account.recoverMessage(text=message,vrs=(v,r,s))
        return address
       

