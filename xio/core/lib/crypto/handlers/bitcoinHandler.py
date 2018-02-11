#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .common import *

import bitcoin

class BitcoinEthereumHandler:

    def __init__(self,private=None,seed=None):

        if private:
            priv = private
        elif seed:
            priv = sha3_keccak_256( seed )
        else:
            seed = uuid.uuid4().hex
            master_key = bitcoin.bip32_master_key(seed.encode())
            key = bitcoin.bip32_extract_key(master_key)
            key = key[:-2] # https://github.com/vbuterin/pybitcointools/issues/111
            priv = key

        # private
        assert priv
        assert len(priv)==64

        # public
        pub = bitcoin.privtopub(decode_hex(priv))
        pub = pub[1:]
        assert pub
        assert len(pub)==64

        # address
        self.private = priv
        self.public = encode_hex(pub)
        self.address = self.pub2EthereumAddress(self.public)
        assert len(self.address)==42


    def sign(self,message): 
        sig = bitcoin.ecdsa_sign(message,self.private)
        assert self.recover(message,sig)==self.address
        return sig

    @staticmethod
    def recover(message,sig): 
        pub = bitcoin.ecdsa_recover(message, sig) 
        pub = pub[2:] # pub already hex encoded
        return self.pub2EthereumAddress(pub)
        

    @staticmethod
    def pub2EthereumAddress(pub):
        pub = decode_hex(pub)
        pub = pub[1:] if len(pub)==65 else pub
        assert len(pub)==64
        address = decode_hex(sha3_keccak_256(pub))[12:]
        address = "0x"+encode_hex(address)
        return str_to_bytes(address)


class BitcoinHandler:

    def __init__(self,private=None,seed=None):

        if private:
            priv = private
        elif seed:
            priv = encode_hex( sha3_256( seed ) )
        else:
            seed = uuid.uuid4().hex
            self._master_key = bitcoin.bip32_master_key(seed.encode())
            self._key = bitcoin.bip32_extract_key(master_key)
            key = key[:-2] 
            priv = key

        # private
        assert priv
        assert len(priv)==64

        # public
        pub = bitcoin.privtopub(decode_hex(priv))
        pub = pub[1:]
        assert pub

        # address
        self.private = priv
        self.public = encode_hex(pub)
        self.address = self.pub2address(self.public)
        

    def sign(self,message): 
        sig = bitcoin.ecdsa_sign(message,self.private)
        assert self.recover(message,sig)==self.address
        return sig

    @staticmethod
    def recover(message,sig): 
        pub = bitcoin.ecdsa_recover(message, sig) 
        pub = pub[2:] # pub already hex encoded
        return BitcoinHandler.pub2address(pub)
        

    @staticmethod
    def pub2address(pub):
        pub = decode_hex(pub)
        address = bitcoin.pubtoaddress(decode_hex(priv))
        return address


