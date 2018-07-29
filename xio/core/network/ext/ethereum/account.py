#!/usr/bin/env python
# -*- coding: utf-8 -*-


from xio.core.lib.crypto.common import *

assert sha3_keccak_256 #tofix, this line is to prevent uwsgi error on python2.7 (sha3_keccak_256 == None)

try:
    import web3
    WEB3_HANDLER = web3.__version__.startswith('4.')
except Exception as err:
    WEB3_HANDLER = False


try:
    import bitcoin
    BITCOIN_HANDLER = True
except Exception as err:
    BITCOIN_HANDLER = False


def account(*args,**kwargs):
    #h = BitcoinEthereumHandler if BITCOIN_HANDLER else Web3Handler
    h = Web3Handler if WEB3_HANDLER else BitcoinEthereumHandler 
    return h(*args,**kwargs)

Account = account

class _Account:

    def __init__(self,*args,**kwargs):
        self.ethereum = kwargs.get('ethereum')
        try: 
            self.address = to_string(self.address)
            import web3
            self.address = web3.Web3('').toChecksumAddress(self.address)  
        except Exception as err:
            print ('ETHEREUM ERROR', err)
 
   
    def getBalance(self):
        return self.ethereum.getBalance(self.address)

    def send(self,dst,value):
        transaction = {
            'from': self.address,
            'to': dst,
            'value': value
        }
        return self.web3.sendRawTransaction(transaction,self.key._private)



class Web3Handler(_Account):

    def __init__(self,private=None,seed=None):
        
        self._web3 = web3.Web3('')
        try:
            self._web3.eth.enable_unaudited_features()
        except:
            pass
        if private:
            self._account = self._web3.eth.account.privateKeyToAccount(private)
            self.private = private
            self.address = account.address
        elif seed:
            priv = sha3_keccak_256( seed )
            priv = decode_hex(priv)
            self._account = self._web3.eth.account.privateKeyToAccount(priv)
            self.private = self._account.privateKey.hex()[2:]
        else:
            self._account = self._web3.eth.account.create()
            self.private = self._account.privateKey.hex()[2:]
   
        self.address = self._account.address
        self.address = self._web3.toChecksumAddress(self.address) 

    
    def sign(self,message):
        sig = self._account.sign(message_text=message)
        v = sig.v
        r = sig.r.hex()
        s = sig.s.hex()
        return (v,r,s)

    def recover(self,message,sig): 
        (v,r,s) = sig
        address = self._web3.eth.account.recoverMessage(text=message,vrs=(v,r,s))
        return address
       

    @classmethod    
    def recoverToken(cls,token):
        nfo = token
        if token.count('-') > 2:
             (id,nonce,v,r,s) = token.split('-')
             print ('WARNING - VERIFY NOT IMPLEMENTED')
             return id
             """
             sig = (v,r,s)
             from ethereum.utils import ecrecover_to_pub
             from rlp.utils import decode_hex
             #print ecrecover_to_pub(nonce,int(decode_hex(v[2:])),decode_hex(r[2:]),decode_hex(s[2:]))
             """
        else:
            print( token )
            nonce,sig = token.split('-')
        address = cls.recover(nonce,sig)
        return address

   
    def generateToken(self):
        import time
        nonce = str(int(time.time()))
        v,s,r = self.sign(nonce)
        token = '%s-%s-%s-%s-%s' % (self.address,nonce,v,r,s)
        assert self.recoverToken(token).lower()==self.address.lower()
        return token


class BitcoinEthereumHandler(_Account):

    def __init__(self,private=None,seed=None,**kwargs):

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
        pub = bitcoin.privtopub(decode_hex(priv)) ########## BUG SEGMENTATION FAULT PYTHON3
        pub = pub[1:]

        assert pub
        assert len(pub)==64

        # address
        self.private = priv
        self.public = encode_hex(pub)

        
        self.address = self.pub2EthereumAddress(self.public)
        assert len(self.address)==42

        _Account.__init__(self,**kwargs)


    def sign(self,message): 
        sig = bitcoin.ecdsa_sign(message,self.private)
        assert self.recover(message,sig).lower()==self.address.lower()
        return sig

    @classmethod
    def recover(cls,message,sig): 
        pub = bitcoin.ecdsa_recover(message, sig) 
        pub = pub[2:] # pub already hex encoded
        return cls.pub2EthereumAddress(pub)
        

    @classmethod
    def pub2EthereumAddress(cls,pub):
        pub = decode_hex(pub)
        pub = pub[1:] if len(pub)==65 else pub
        assert len(pub)==64
        address = decode_hex(sha3_keccak_256(pub))[12:]
        address = "0x"+encode_hex(address)
        return str_to_bytes(address)


    def generateToken(self):
        import time
        nonce = str(int(time.time()))
        sig = self.sign(nonce)
        token = nonce+'-'+sig
        assert self.recoverToken(token).lower()==self.address.lower()
        return token


    @classmethod    
    def recoverToken(cls,token):
        nfo = token
        if token.count('-') > 2:
             (id,nonce,v,r,s) = token.split('-')
             print ('WARNING - VERIFY NOT IMPLEMENTED')
             return id
             """
             sig = (v,r,s)
             from ethereum.utils import ecrecover_to_pub
             from rlp.utils import decode_hex
             #print ecrecover_to_pub(nonce,int(decode_hex(v[2:])),decode_hex(r[2:]),decode_hex(s[2:]))
             """
        else:
            nonce,sig = token.split('-')
        address = cls.recover(nonce,sig)
        return address


    def signTransaction(self,data):
        ethereum = self.ethereum
        if not ethereum:
            from .connector import Connector
            ethereum = Connector()
        return ethereum.transaction(data).sign(self.private)



        
