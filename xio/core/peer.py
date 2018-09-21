#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import resource

from .lib.crypto import crypto

from xio.core.lib.utils import generateuid, to_string


class Peer(resource.Resource):

    #__XMETHODS__ = False #1803 - commented for network case, why False ?

    key = None
    name = None
    id = None
    token = None
    network = None
    uuid = None

    def __init__(self, id=None, network=None, **kwargs):

        token = kwargs.pop('token', None)
        seed = kwargs.pop('seed', None)
        key = kwargs.pop('key', None)

        if id:
            self.key = None
            self.id = id
            self.token = None
        elif key or seed or token == None:
            self.key = crypto.key(priv=key, token=token or None, seed=seed)
            self.id = self.key.address
            self.token = self.key.token
        elif token:
            self.key = crypto.key(token=token)
            self.id = self.key.address
            self.token = token

        self.uuid = generateuid()

        resource.Resource.__init__(self, **kwargs)

        import xio
        from .peers import Peers
        self.peers = Peers(peer=self)
        self.network = xio.context.network

    @classmethod
    def factory(cls, *args, **kwargs):

        if args:
            id = args[0]
            if len(args) > 1:
                context = args[1]
            else:
                context = {}
        else:
            id = kwargs.pop('id', None)
            context = {}
        if id:
            import xio
            return resource.resource(id, context, client=xio.context.user)
        else:
            _cls = kwargs.pop('_cls', None)
            cls = _cls if _cls else cls
            return cls(**kwargs)

    def connect(self, peer):
        assert peer and isinstance(peer, resource.Resource)
        cli = resource.resource(peer, client=self)
        return cli

    def encrypt(self, message, dst_public_key=None):
        return self.key.encryption.encrypt(message, dst_public_key=dst_public_key)

    def decrypt(self, message):
        return self.key.encryption.decrypt(message)
