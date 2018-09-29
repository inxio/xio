#!/usr/bin/env python
#-*- coding: utf-8 -*--

from xio.core.lib.crypto.crypto import sha256, sha3_keccak_256, encode_hex, decode_hex, Key, to_string

import unittest

TEST_SEED = b'very weak seed'
TEST_SHA256 = b'c55487a5417d759e04f5d57d34e11151e2fc04a2048c8b19dca9ed3c59a8a49e'
TEST_SHA3_KECCAK_256 = b'37b75e9adbf125f93fb14b41cb4fe530e6dd6e4a9c854ab1b33c513cc561e05b'

TEST_PRIVATE = b'c55487a5417d759e04f5d57d34e11151e2fc04a2048c8b19dca9ed3c59a8a49e'
TEST_PUBLIC = b'145a1afd1792a23c79eb267ec53ae02117d44a13659cb44f7ec4de3579bbf8a7'
TEST_ADDRESS = TEST_PUBLIC.decode()


TEST_ETHEREUM_PRIVATE = b'ef62ee9dee29b728a62ae606299fe8d1100cdf878a02b04a944d70f2627a5875'
TEST_ETHEREUM_ADDRESS = u'0x3ec381e7291d7058ac13fe74998cd02d580500d2'


class TestCases(unittest.TestCase):

    def test_base(self):

        assert sha256(TEST_SEED) == TEST_SHA256
        if sha3_keccak_256:
            assert sha3_keccak_256(TEST_SEED) == TEST_SHA3_KECCAK_256

        key = Key()
        assert key.private
        assert len(key.private) == 64
        assert key.public
        assert len(key.public) == 64
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
        assert key.address.lower() == TEST_ADDRESS.lower()  # toChecksumAddress in python2 ?

    def test_from_seed(self):

        k1 = Key(seed=TEST_SEED)
        k2 = Key(seed=TEST_SEED)
        k3 = Key(seed=b'other seed')

        assert k1.private == TEST_PRIVATE
        assert k1.public == TEST_PUBLIC
        assert k1.address == TEST_ADDRESS

        assert k1.private == k2.private
        assert k1.private != k3.private

    def test_from_token(self):

        k1 = Key()
        assert k1.token
        assert to_string(k1.recoverToken(k1.token)) == k1.address

        k2 = Key(token=k1.token)
        assert k2.address == k1.address

    def test_encryption(self):

        key1 = Key()
        message = b'mysecret'
        crypted = key1.encrypt(message)
        assert crypted and crypted != message
        assert key1.decrypt(crypted) == message

        key2 = Key()
        crypted = key1.encrypt(message, key2.encryption.public)
        assert crypted and crypted != message
        assert key2.decrypt(crypted) == message
        with self.assertRaises(Exception):
            key1.decrypt(crypted) == message

    def test_ethereum(self):
        key = Key(seed=TEST_SEED)
        ethereumaccount = key.account('xio/ethereum')
        if ethereumaccount:
            assert ethereumaccount.private.lower() == TEST_ETHEREUM_PRIVATE
            assert ethereumaccount.address.lower() == TEST_ETHEREUM_ADDRESS

    def test_jwt_token(self):

        key = Key(seed=TEST_SEED)

        token = key.generateToken('xio', {'scope': 'ok'})
        assert key.recoverToken(token).get('body').get('iss') == key.address == TEST_ADDRESS

        token = key.generateToken('xio/ethereum', {'scope': 'ok'})
        print(key.recoverToken(token))
        assert key.recoverToken(token).get('body').get('iss').lower() == TEST_ETHEREUM_ADDRESS

if __name__ == '__main__':

    unittest.main()
