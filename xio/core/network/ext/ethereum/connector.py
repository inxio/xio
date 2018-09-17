#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path

import json
import sys
from pprint import pprint

from .account import Account
from .contract import Contract

try:
    import web3
    WEB3VERSION = int(web3.__version__.split('.').pop(0))
except Exception as err:
    WEB3VERSION = 0

try:
    import socket
    socket.gethostbyname('ethereum')
    ETHEREUM_ENDPOINT = 'http://ethereum:8545'
except socket.error:
    ETHEREUM_ENDPOINT = None


import xio
ETH_DEFAULT_ENDPOINT = xio.env.get('ethereum', 'http://localhost:8545')


class Connector:

    WEB3VERSION = WEB3VERSION
    OLDWEB3VERSION = WEB3VERSION < 4

    def __init__(self,network='local',user=None):

        from web3 import Web3, HTTPProvider
        print(network)
        if network=='local':
            endpoint = ETH_DEFAULT_ENDPOINT
        elif network=='ropsten':
            endpoint = 'https://ropsten.infura.io/'
        elif network=='mainnet':
            endpoint = 'https://mainnet.infura.io/'
        else:
            endpoint = network

        self.endpoint = endpoint
        self.web3 = Web3(HTTPProvider(self.endpoint))
        
        try:
            self.web3.eth.enable_unaudited_features()
        except:
            pass # old version ?    
        try:
            # tofix : prevent no endpoint availbale
            self.network = self.web3.version.network
            self.gasprice = self.web3.eth.gasPrice
            self.blockNumber = self.web3.eth.gasPrice
        except:
            pass
        self._defaultaccount = self.account(user) if user else None
        
        
    def account(self,*args,**kwargs):
        if args and hasattr(args[0],'key'):
            user = args[0]
            account = user.key.account('ethereum')
            account.ethereum = self # need to use copy or regenrate new account
            return account
        return Account(self,*args,**kwargs)
         
    def contract(self,**kwargs):
        kwargs.setdefault('account',self._defaultaccount)
        return Contract(self,**kwargs)

    def getBalance(self,address):
        return self.web3.eth.getBalance(address)

    def transactions(self,address=None,filter=None):
        if self.OLDWEB3VERSION:
            filter = {'fromBlock': 'earliest', 'toBlock': 'latest', 'address': address} #,'address': self.address
            return self.web3.eth.filter(filter).get(only_changes=False)
            #return []

    def about(self):
        about = {
            'endpoint': self.endpoint,
            'network': self.web3.version.network,
            'blockNumber': self.web3.eth.blockNumber,
            'gasPrice': self.web3.eth.gasPrice,
            'coinbase': self.web3.eth.coinbase,
        }      
        return about    

    def transaction(self,data):
        return Transaction(self,data)



    def sendRawTransaction(self,raw):
        tx = self.web3.eth.sendRawTransaction(raw) 
        return tx
        """    
        # not ready for parsing response/logs 
        receipt = ethereum.web3.eth.getTransactionReceipt(tx)
        log = receipt.get('logs')[0]
        pprint(dict(log))
        """

        

class Transaction:

    def __init__(self,ethereum,data):
        self.ethereum = ethereum
        self.web3 = self.ethereum.web3
        self.data = data or {}
        data.update({
            'gasPrice': '2345678',
            'gas': 3100000,
            #'chainId': '1',
            'nonce': self.web3.eth.getTransactionCount(data.get('from')),
            'gasPrice': self.web3.eth.gasPrice
        })
        data.setdefault('value',0)
        self.raw = None
        
        
    def sign(self,key):

        from xio.core.lib.utils import decode_hex,to_bytes

        if self.ethereum.OLDWEB3VERSION:
            import rlp
            from ethereum.transactions import Transaction

            # ethereum.transactions not check if data is already 0x.. encoded
            data = self.data.get('data') # '0x...'
            data = bytes( decode_hex(data[2:]) )

            tx = Transaction(
                nonce       = self.data.get('nonce'),
                gasprice    = self.data.get('gasPrice'),
                startgas    = self.data.get('gas'),
                to          = self.data.get('to'),
                value       = self.data.get('value'),
                data        = data,
            )
            #key = b'b26c4bf3a911c0eaafaedee9ce3ba2c7cf3fa4988eccdafc9fa908ab1e7e7c33'
            #pprint(tx.to_dict())
            tx.sign(key)
            raw_tx = rlp.encode(tx)
            raw_tx_hex = self.ethereum.web3.toHex(raw_tx)
            self.raw = raw_tx_hex
        else:
            # http://web3py.readthedocs.io/en/latest/web3.eth.account.html
            key = decode_hex(key)
            signed = self.web3.eth.account.signTransaction(self.data,key)
            self.raw = signed.get('rawTransaction')


        return self.raw


    def send(self):
        return self.ethereum.sendRawTransaction(self.raw)  
        

