#!/usr/bin/env python
#-*- coding: utf-8 -*--

from xio.core.lib.crypto.crypto import sha3_256, encode_hex, decode_hex, Key

import unittest

TEST_PRIV = '0c264f53af4ac2b4da6c5748e8173d770a3b1ad8564bbe74c5c4aeaa0d5b639c'
TEST_PUB = '8f334d35c7203478f34e5f12ee43ee6bc9e1c3b6be4536f8a28a1b093c77f18f0308f0be7c5d7aa6c7770bbda9f7b05e6863709d3dcc59843a42c68783308a22'
TEST_ADDRESS = '0x7D6945e959303CBd4eFE06caB90ED67bA197D520'


class TestCases(unittest.TestCase):


    def test_base(self):

        assert encode_hex( sha3_256(b'') ) == 'c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'

        key = Key()
        assert key._private
        assert len(key._private)==64
        assert key.public
        assert len(key.public)==128
        assert key.address
        assert len(key.address)==42

    def test_from_scratch(self):
        key = Key()
        assert key._private
        assert key.public
        assert key.address

    def test_from_private(self):
        key = Key(priv=TEST_PRIV)
        assert key.public == TEST_PUB
        assert key.address.lower() == TEST_ADDRESS.lower() # toChecksumAddress in python2 ?
        
    def test_from_seed(self):
        seed = 'weak seed'
        k1 = Key(seed=seed)
        k2 = Key(seed=seed)
        k3 = Key(seed='other seed')
        assert k1._private == '7e4e69084b5bfaf732fe661c29d824233c801b1a7732430bb94d73805506fb8c'
        assert k1.address.lower() == '0x211C7ea94d7bdbb19F41B5b096a01CB349981559'.lower()
        assert k1._private == k2._private
        assert k1._private != k3._private

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
        



if __name__ == '__main__':

    unittest.main()






