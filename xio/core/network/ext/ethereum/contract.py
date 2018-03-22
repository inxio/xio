#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import json
import sys
from pprint import pprint

import xio


class ContractMethodWrapper:

    def __init__(self,contract,method):
        self.contract = contract 
        self.method = method 

    def __call__(self,*args,**kwargs):
        print( 'CONTRACT CALL',self.method,args,kwargs)
        return self.contract.request(self.method,*args,**kwargs)



class Contract:

    def __init__(self,ethereum=None,abi=None,address=None,bytecode=None,filepath=None,source=None,name=None,account=None):
        self.ethereum = ethereum
        self.account = account
        self.web3 = self.ethereum.web3
        self.address = address
        self.name = name 
        self.abis = {}
        self.abi = abi
        self.api = {}

        if self.address:
            self.c = self.web3.eth.contract(abi=self.abi,address=self.address)
            for row in self.abi:
                name = row.get('name','')
                self.api[ name.lower() ] = row  
                if row.get('type')=='function':
                    h = ContractMethodWrapper(self,name) 
                    setattr(self,name.lower(), h)   # binding for request
                    setattr(self,name, h)           # binding for direct use



    def events(self,name=None,filter=None):
        """
        # http://web3py.readthedocs.io/en/latest/contracts.html


        # ceci ne fonctionne pas : AttributeError: 'Contract' object has no attribute 'events
        tx_hash = contract.functions.myFunction(12345).transact({'to':contract_address})
        >>> tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
        >>> rich_logs = contract.events.myEvent().processReceipt(tx_receipt)
        >>> rich_logs[0]['args']
        """
        params = {
            'fromBlock': 0, 
            'toBlock': 'latest'
        }
        if ethereum.OLDWEB3VERSION:
            # http://web3py.readthedocs.io/en/stable/contracts.html
            events = self.c.pastEvents(name, params) #
            rows = events.get(only_changes=False)

        else:
            params = {
                
            }
            events = self.c.eventFilter(name, params)
            rows = events.get_all_entries()
            print (rows)

        for row in rows:
            if filter:
                check = [ row.get(k)==v for k,v in filter.items() ]
                if all(check):
                    yield row
            else:
                yield row

        

    def transaction(self,_from,method,args):

        """
        v3 https://github.com/ethereum/web3.py/blob/v3/web3/contract.py
        """    

        abi = self.api.get(method.lower())
        assert abi
        name = abi.get('name')

        if self.ethereum.OLDWEB3VERSION:
            data = self.c._encode_transaction_data(name,args)
        else:
            data = self.c.encodeABI(method, args)

        transaction = self.ethereum.transaction({
            'from': _from,
            'to': self.address,
            #'gasPrice': 2345678921,
            #'gas': 200000,
            #'nonce': nonce,
            'data': data
        })
        return transaction


    def request(self,method,args=[],context={}):

        print( 'CONTRACT REQUEST',method,args,context)

        _from = context.get('from')

        if hasattr(_from,'key'):
            account = self.ethereum.account(_from)
            private = account.private
            context['from'] = account.address


        # fix for uppercase method handling (req)

        method = method.lower() 
        abi = self.api.get(method)
        assert abi
        name = abi.get('name')

        USE_TRANSACTION = not abi.get('constant')


        if self.ethereum.OLDWEB3VERSION:
            print( 'WARNING USING OLD')
            if not USE_TRANSACTION:
                h = getattr( self.c.call(transaction=context) ,name)
            else:
                if not private:
                    h = getattr( self.c.transact(transaction=context) ,name)

                transaction = self.transaction(context['from'],name,args)
                transaction.sign(private)
                return transaction.send()
            
            return h(*args)


        # fix Address has an invalid EIP checksum 
        # web3.utils.checkAddressChecksum    
        """
        context['from'] = self.web3.toChecksumAddress(context['from'])
        if 'to' in context:
            context['to'] = self.web3.toChecksumAddress(context['to'])
        """

        if not USE_TRANSACTION:
            methodhandler = getattr( self.c.call(context) , name)
            return methodhandler(*args)
        else:
            if not private:
                context.setdefault('gas',2000000) # fix bug gas
                methodhandler = getattr( self.c.transact(context) , name)
                return methodhandler(*args)
            else:
               
                transaction = self.transaction(context['from'],name,args)
                transaction.sign(private)
                return transaction.send()
           





