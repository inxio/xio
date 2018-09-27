#!/usr/bin/env python
# -*- coding: utf-8 -*-


from xio.core.lib.crypto.common import *

assert sha3_keccak_256  # tofix, this line is to prevent uwsgi error on python2.7 (sha3_keccak_256 == None)

try:
    import web3
except Exception as err:
    print('web3 not found')


def account(*args, **kwargs):
    return Web3Handler(*args, **kwargs)

Account = account


class _Account:

    def __init__(self, *args, **kwargs):
        self.ethereum = kwargs.get('ethereum')
        try:
            self.address = to_string(self.address)
            import web3
            self.address = web3.Web3('').toChecksumAddress(self.address)
        except Exception as err:
            print('ETHEREUM ERROR', err)

    def getBalance(self):
        return self.ethereum.getBalance(self.address)

    def send(self, dst, value):
        transaction = {
            'from': self.address,
            'to': dst,
            'value': value,
            'data': ''
        }
        print(transaction)
        transaction = self.ethereum.transaction(transaction)
        transaction.sign(self.private)
        tx = transaction.send()
        print(tx)
        return tx


class Web3Handler(_Account):

    def __init__(self, private=None, seed=None):

        self._web3 = web3.Web3('')

        if private:
            self._account = self._web3.eth.account.privateKeyToAccount(private)
            self.private = private
            self.address = account.address
        elif seed:
            priv = sha3_keccak_256(seed)
            priv = decode_hex(priv)
            self._account = self._web3.eth.account.privateKeyToAccount(priv)
            self.private = self._account.privateKey.hex()[2:]
        else:
            self._account = self._web3.eth.account.create()
            self.private = self._account.privateKey.hex()[2:]

        self.address = self._account.address
        self.address = self._web3.toChecksumAddress(self.address)

    def sign(self, message):
        from eth_account.messages import defunct_hash_message
        message_hash = defunct_hash_message(text=message)
        signed_message = self._web3.eth.account.signHash(message_hash, private_key=self.private)
        return signed_message.signature.hex()

    @staticmethod
    def recover(message, sig):
        from eth_account.messages import defunct_hash_message
        message_hash = defunct_hash_message(text=message)
        address = web3.Web3('').eth.account.recoverHash(message_hash, signature=sig)
        return address
