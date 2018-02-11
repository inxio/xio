#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xio.core.lib.utils import is_int, is_string, str_to_bytes, decode_hex, encode_hex, to_string 

import uuid


# SHA256

import nacl.hash
def sha256(x): 
    return nacl.hash.sha256(x)

# SHA3 KECCAK 256
sha3_keccak_256 = None
try:
    from Crypto.Hash import keccak
    def sha3_keccak_256(x): 
        h = keccak.new(digest_bits=256, data=x).hexdigest()
        return str_to_bytes(h)

except ImportError:
    try:
        import sha3 as _sha3
        def sha3_keccak_256(x): 
            h = _sha3.keccak_256(x).hexdigest()
            return str_to_bytes(h)
    except:
        pass

