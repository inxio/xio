#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xio
import json
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

    def __init__(self, config):

        ethereum_network = config.get('ethereum').get('network')
        abi = config.get('ethereum').get('abi')
        address = config.get('ethereum').get('address')
        coinbase = config.get('ethereum').get('coinbase')

        # DHT
        from .ext.dht.service import DhtService
        #import xio
        #bootstrap = xio.env('network')
        self.dht = None
        try:
            # dht require python3
            dhtbootstrap = xio.env.get('dht')
            if dhtbootstrap:
                self.dht = DhtService(bootstrap=dhtbootstrap)
        except Exception as err:
            print(err)


        # IPFS
        from .ext.ipfs.connector import Connector
        self.ipfs = Connector(endpoint=config.get('ipfs'))

        # ETHEREUM
        from .ext.ethereum.connector import Connector
        user = xio.user(seed='root')
        self.ethereum = Connector(network=ethereum_network, user=user)

        self.log = xio.log
        self._about = {}

        if address and not abi:
            # fetch about network
            tmpcontract = self.ethereum.contract(address=address, abi=BASEABI)
            ipfshash = tmpcontract.request('about')
            assert ipfshash
            from xio.core.network.ext.ipfs.connector import Connector
            ipfs = Connector()
            about = ipfs.get(ipfshash)
            import json
            self._about = json.loads(about)
            abi = self._about.get('abi')
            assert abi

        self.contract = self.ethereum.contract(address=address, abi=abi) if address else None
        adminuser = xio.user(seed='root')
        self.contract.account = self.ethereum.account(adminuser)

        self._handler_api = {}
        for m in dir(self):
            if m[0] != '_':
                h = getattr(self, m)
                if callable(h):
                    self._handler_api[m.lower()] = h

    def about(self):
        about = self._about
        if self.contract:
            about.update({
                'address': self.contract.address,
                #'abi': self.contract.abi
            })
        return about

    def start(self, app):
        self.log.info('==== start network =====', self)
        if self.dht:
            self.dht.start()

    def __call__(self, req):

        self.log.info('==== XIO NETWORK REQUEST =====', req)

        # require ethereum account based authentication
        req.require('auth', 'xio/ethereum')

        if req.ABOUT:
            return self.about()

        # pprint(req._debug())

        # check for method handler
        method = req.xmethod or req.method

        h = self._handler_api.get(method.lower())
        # print(self._handler_api)
        if h:
            return h(req)
        elif method.lower() in self.contract.api:
            # check for transaction
            api = self.contract.api.get(method.lower())
            # get real name (case sensitive)
            method = api.get('name')
            # build args
            args = []
            for param in api.get('inputs'):
                args.append(req.path if not args and req.path else req.data)  # tofix : clarify args for xmethod + bug with int/str path check
            # check for transaction
            require_transaction = not api.get('constant')
            if not require_transaction:
                # call contract and send result
                ctx = {
                    'from': req.client.id
                }
                return self.contract.request(req.xmethod, args, ctx)
            else:
                # prepare transaction

                # print req.content_type
                print('=====TRANS', method, args)

                transaction = self.contract.transaction(req.client.id, method, args)
                pprint(transaction.data)

                # require ethereum signature
                signature = req.client.auth.require('signature', 'xio/ethereum', transaction.data)
                tx = self.ethereum.sendRawTransaction(signature)
                return tx

        # check for path handler
        p = req.path.split('/')
        if p and hasattr(self, p[0]):
            name = p.pop(0)
            h = getattr(self, name)
            req.path = '/'.join(p)
            return h(req)
