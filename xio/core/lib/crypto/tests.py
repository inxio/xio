#!/usr/bin/env python
#-*- coding: utf-8 -*--

from xio.core.lib.crypto.crypto import sha3_keccak_256, encode_hex, decode_hex, Key, to_string

import unittest

TEST_SEED       = b'very weak seed'
TEST_SHA256     = b'37b75e9adbf125f93fb14b41cb4fe530e6dd6e4a9c854ab1b33c513cc561e05b'

TEST_PRIVATE    = b'37b75e9adbf125f93fb14b41cb4fe530e6dd6e4a9c854ab1b33c513cc561e05b'
TEST_PUBLIC     = b'2f8527d027626f176a31b1818bdba6c51d0d0aa6f3b54d715c18c3ce1d5fc77f'
TEST_ADDRESS    = TEST_PUBLIC

TEST_ETHEREUM_ADDRESS = b'0xf05c29f39956dff46827c24392f8c2ed0b3c951b' 

key = Key(priv=TEST_PRIVATE)

class TestCases(unittest.TestCase):


    def test_base(self):

        assert encode_hex( sha3_keccak_256(TEST_SEED) )  == TEST_SHA256.decode()

        key = Key()
        assert key.private
        assert len(key.private)==64
        assert key.public
        assert len(key.public)==64
        assert key.address
        #assert len(key.address)==42

    def test_from_scratch(self):
        key = Key()
        assert key.private
        assert key.public
        assert key.address

    def test_from_private(self):
        key = Key(priv=TEST_PRIVATE)
        assert key.public == TEST_PUBLIC
        assert key.address.lower() == TEST_ADDRESS.lower() # toChecksumAddress in python2 ?
        
    def test_from_seed(self):
        
        k1 = Key(seed=TEST_SEED)
        k2 = Key(seed=TEST_SEED)
        k3 = Key(seed='other seed')

        assert k1.private == TEST_PRIVATE
        assert k1.public == TEST_PUBLIC
        assert k1.address == TEST_ADDRESS

        assert k1.private == k2.private
        assert k1.private != k3.private

    def test_from_token(self):
        
        k1 = Key()
        assert k1.token
        assert k1.recoverToken(k1.token)==k1.address
        
        k2 = Key(token=k1.token)
        assert k2.address == k1.address


    def test_encryption(self):
        
        key1 = Key()
        message = b'mysecret'
        crypted = key1.encrypt(message)
        assert crypted and crypted != message
        assert key1.decrypt(crypted)==message

        key2 = Key()
        crypted = key1.encrypt(message,key2.encryption.public)
        assert crypted and crypted != message
        assert key2.decrypt(crypted)==message
        with self.assertRaises(Exception):
            key1.decrypt(crypted)==message
        

    def test_ethereum(self):
        
        key = Key(priv=TEST_PRIVATE)
        if key.ethereum:
            #print (key.ethereum.address)
            #assert key.ethereum.private == TEST_ETHEREUM_PRIVATE.decode()
            assert key.ethereum.address == TEST_ETHEREUM_ADDRESS.decode()


if __name__ == '__main__':

    unittest.main()






