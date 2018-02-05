#!/usr/bin/env python
#-*- coding: utf-8 -*--

import xio
import unittest

def checkPeer(peertype):

    factory = getattr(xio,peertype)
    assert factory

    assert factory().id != factory().id, Exception('ERROR GENETERATE UID %s' % peertype)

    # server instance    
    seed = 'myseed%s' % peertype
    assert factory(seed=seed).id == factory(seed=seed).id
    peer = factory()
    assert peer.id
    assert peer.id
    assert peer.token
    assert peer.key
    assert peer.key._private
    assert peer.key.public
    assert peer.key.address

    # client instance using server instance .. eg xio.app( app )
    from xio.core import resource
    cli = factory(peer)
    assert cli and cli.__class__.__name__.lower()=='resource', Exception('ERROR FACTORY %s' % peertype)
    assert cli.about().content.get('id')==peer.id, Exception('ERROR FACTORY %s' % peertype)

    # client instance using id/xrn
    cli = factory(peer.id)
    assert cli and cli.__class__.__name__.lower()=='resource'
    #assert cli.about().content.get('id')==peer.id, Exception('ERROR FACTORY %s' % peertype) ################### TOFIX

    # peer about
    assert peer.about().content.get('id')==peer.id
    assert peer.about().content.get('type')==peertype
    cli = xio.resource(peer)
    assert cli.about().content.get('id')==peer.id
    assert cli.about().content.get('type')==peertype

    # peer connection
    user = xio.user()
    cli = user.connect(peer)
    assert cli.context.get('client').id == user.id

    app = xio.app(seed='myapp')
    app.put('www',lambda req: req._debug() )
    cli = peer.connect(app)
    info = cli.get().content
    assert info.get('client').get('id')==peer.id


