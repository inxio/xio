#!/usr/bin/env python
#-*- coding: utf-8 -*--

import unittest

from .connector import Connector
from .account import Account

import xio

root = xio.user(seed='root')

ethereum = Connector()


class TestCases(unittest.TestCase):


    def test_base_connector(self):

        assert ethereum.endpoint
        assert ethereum.network
        assert ethereum.gasprice
        
        about = ethereum.about()
        
        assert about.get('blockNumber')
        assert about.get('gasPrice')


    def test_base_account(self):

        # account from scratch
        account = Account(seed='root')
        assert account.private
        assert account.address
        assert ethereum.getBalance(account.address)>=0

        # account by xio.user derivation
        assert ethereum.getBalance(root.key.account('ethereum').address)>0

        # account/network conversion
        account = ethereum.account(root)
        assert account.getBalance()>0
        
    def _test_base_account(self):

        root = Account(seed=root)

        user1 = ethereum.account()
        assert user1.getBalance()==0

        user2 = ethereum.account(priv=key)
        assert user2.send(user1.address, 2000000000000000)
        assert user1.getBalance()==2000000000000000

        user3 = ethereum.account()
        assert user1.send(user3.address, 120)
        assert user3.getBalance()==120

    def _test_contract(self):
        import os
        import json
        jsonfilepath = os.path.dirname(os.path.realpath(__file__))+'/contracts/test/latest/test.json'
        with open(jsonfilepath) as f:
            data = json.load(f)
        abi = data.get('abi').get('Test')
        address = data.get('addresses').get('test')

        assert abi
        assert address
        import xio
        contract = ethereum.contract(abi=abi,address=address)
        assert contract


        # direct contract handler (not a resource) 
        assert contract.request('getValue',**{'from':user.address}) in (123,456) 
        """
        # resource wrapper 
        assert testcontract.request('getValue',**{'_from':TEST_USER_ROOT.address}).content in (123,456) 
        
        # transactions
        assert testcontract.contract.request('setValue',456,**{'from':TEST_USER_ROOT.address})
        assert testcontract.contract.request('getValue',**{'from':TEST_USER_ROOT.address})==456

        # raw transactions
        assert testcontract.contract.request('setValue',456,**{'from':TEST_USER_ROOT.address})
        assert testcontract.contract.request('getValue',**{'from':TEST_USER_ROOT.address})==456
        """





if __name__ == '__main__':

    unittest.main()



