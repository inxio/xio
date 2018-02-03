#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://pynacl.readthedocs.io/en/stable/public/

from .common import *

import nacl.utils
from nacl.public import PrivateKey, PublicKey, SealedBox

class NaclHandler:

    def __init__(self,private=None,seed=None):
        self._private = PrivateKey( sha3_256( private ) )
        self.public = self._private.public_key


    def encrypt(self,message,dst_public_key=None):
        dst_public_key = dst_public_key or self.public
        sealed_box = SealedBox(dst_public_key)
        encrypted = sealed_box.encrypt(to_string(message))
        return encode_hex(encrypted)

    def decrypt(self,message):
        unseal_box = SealedBox(self._private)
        message = unseal_box.decrypt(decode_hex(message))
        return message

