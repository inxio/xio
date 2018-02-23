#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint



BASEABI = [{
    "constant": True,
    "inputs": [],
    "name": "about",
    "outputs": [
        {
            "name": "",
            "type": "string"
        }
    ],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
}]

class NetworkHandler:

    def __init__(self,address=None,abi=None):
        from xio.ext.ethereum.connector import Connector
        self.ethereum = Connector()
        self._about = {}

        if not abi:
            # fetch about network
            tmpcontract = self.ethereum.contract(address=address,abi=BASEABI)
            ipfshash = tmpcontract.request('about') 
            assert ipfshash
            from xio.ext.ipfs.connector import Connector
            ipfs = Connector()
            about = ipfs.get(ipfshash)
            import json
            self._about = json.loads(about)
            abi = self._about.get('abi')
            assert abi

        self.contract = self.ethereum.contract(address=address,abi=abi)

    def about(self):
        about = self._about
        about.update({
            'address': self.contract.address,
            'api': self.contract.api
        })
        return about


    def __call__(self,req):
    
        req.client.auth.require('scheme', 'xio/ethereum')

        pprint(req._debug())

        if req.ABOUT:
            return self.about()

        elif req.GETBALANCE:
            return self.ethereum.getBalance(req.client.id)

        elif req.SEND:
        
            transaction = self.ethereum.transaction({
                'from': req.client.id,
                'to': req.path,
                'value': req.data
            })
            pprint(transaction.data)
            
            req.client.auth.require('signature', 'xio/ethereum',transaction.data)
            
            transaction.raw = req.data
            tx = transaction.send()
            return tx
        elif req.GETRESOURCE:
           
            args = (req.path,)
            ctx = {
                'from': req.client.id
            }
            return self.contract.request(req.xmethod, *args, **ctx)

        elif req.PUTRESOURCE:
            method = req.xmethod
            args = (req.path,req.data)
            transaction = self.contract.transaction(req.client.id,method,args)

            pprint(transaction.data)

            req.client.auth.require('signature', 'xio/ethereum',transaction.data)

            transaction.raw = req.data
            tx = transaction.send()
            return tx
        elif req.SETTEST:
            method = req.xmethod
            args = (12,)
            transaction = self.contract.transaction(req.client.id,method,args)

            pprint(transaction.data)

            req.client.auth.require('signature', 'xio/ethereum',transaction.data)

            transaction.raw = req.data
            tx = transaction.send()
            return tx
        else:
            print("=====", req)
            ctx = {
                'from': req.client.id
            }
            return self.contract.request(req.xmethod, *req.input, **ctx)
          
            
        return 

       