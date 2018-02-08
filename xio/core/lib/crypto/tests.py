#!/usr/bin/env python
#-*- coding: utf-8 -*--

from xio.core.lib.crypto.crypto import sha3_256, encode_hex, decode_hex, Key

import unittest

TEST_SEED       = 'very weak seed'
TEST_PRIVATE    = '37b75e9adbf125f93fb14b41cb4fe530e6dd6e4a9c854ab1b33c513cc561e05b'
TEST_PUBLIC     = '2f8527d027626f176a31b1818bdba6c51d0d0aa6f3b54d715c18c3ce1d5fc77f'
TEST_ADDRESS    = TEST_PUBLIC

#TEST_PUB = '8f334d35c7203478f34e5f12ee43ee6bc9e1c3b6be4536f8a28a1b093c77f18f0308f0be7c5d7aa6c7770bbda9f7b05e6863709d3dcc59843a42c68783308a22'
#TEST_ADDRESS = '0x7D6945e959303CBd4eFE06caB90ED67bA197D520'



class TestCases(unittest.TestCase):


    def test_base(self):

        assert encode_hex( sha3_256(b'') ) == 'c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'

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
        print(key.public)
        assert key.public == TEST_PUBLIC
        assert key.address.lower() == TEST_ADDRESS.lower() # toChecksumAddress in python2 ?
        
    def test_from_seed(self):
        
        k1 = Key(seed=TEST_SEED)
        k2 = Key(seed=TEST_SEED)
        k3 = Key(seed='other seed')

        print k1.private
        print k1.public

        assert k1.private == TEST_PRIVATE
        assert k1.public == TEST_PUBLIC
        assert k1.address == TEST_ADDRESS

        assert k1.private == k2.private
        assert k1.private != k3.private

    def test_from_token(self):
        
        k1 = Key()
        assert k1.token
        print k1.token
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
        



if __name__ == '__main__':

    unittest.main()






