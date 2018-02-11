#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://pynacl.readthedocs.io/en/stable/public/

from .common import *

import nacl.utils
from nacl.public import PrivateKey, PublicKey, SealedBox, Box
from nacl.signing import SigningKey
import nacl.hash


class NaclEncryptionHandler:

    def __init__(self,naclpriv,naclpub):
        self._naclpriv = naclpriv.to_curve25519_private_key()
        self._naclpub = naclpub.to_curve25519_public_key()
        self.private = self._naclpriv.encode(nacl.encoding.HexEncoder)
        self.public = self._naclpub.encode(nacl.encoding.HexEncoder)


    def encrypt(self,message,dst_public_key=None):
        publicKey = PublicKey( decode_hex(dst_public_key) ) if dst_public_key else self._naclpub
        sealed_box = SealedBox(publicKey)
        encrypted = sealed_box.encrypt(str_to_bytes(message))
        return encode_hex(encrypted)

    def decrypt(self,message):
        unseal_box = SealedBox(self._naclpriv)
        message = unseal_box.decrypt(decode_hex(message))
        return message


class NaclHandler:

    def __init__(self,private=None,seed=None):

        if private:
            self._naclpriv = SigningKey( decode_hex(private) )
        elif seed:
            seed = decode_hex( nacl.hash.sha256( str_to_bytes(seed) ) )
            self._naclpriv = SigningKey( seed )
        else:
            self._naclpriv = SigningKey.generate()
            
        self._naclpub = self._naclpriv.verify_key
        
        self.private = self._naclpriv.encode(nacl.encoding.HexEncoder)
        self.public = self._naclpub.encode(nacl.encoding.HexEncoder)
        self.encryption = NaclEncryptionHandler(self._naclpriv,self._naclpub)


    def sign(self,message):

        signingKey = self._naclpriv
        signed = signingKey.sign(str_to_bytes(message))
        
        verify_key = signingKey.verify_key
        verify_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)

        # check result
        assert message == self.verify(verify_key_hex,encode_hex(signed))
        
        return (str_to_bytes(verify_key_hex),str_to_bytes(encode_hex(signed)))
        

    @staticmethod
    def verify(verify_key_hex,signed):
        verifyKey = nacl.signing.VerifyKey(verify_key_hex, encoder=nacl.encoding.HexEncoder)
        return verifyKey.verify( decode_hex(signed) )

        
