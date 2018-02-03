#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xio.core.lib.utils import is_int, is_string, str_to_bytes, decode_hex, encode_hex, to_string 

import uuid

try:
    from Crypto.Hash import keccak
    def sha3_256(x): 
        return keccak.new(digest_bits=256, data=str_to_bytes(x)).digest()
except ImportError:
    import sha3 as _sha3
    def sha3_256(x): 
        return _sha3.keccak_256(str_to_bytes(x)).digest()

