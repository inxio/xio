#!/usr/bin/env python
#-*- coding: utf-8 -*--
import xio
from xio.core import resource
from xio.core.request import Request, Response

from xio.core.app.app import App
from xio.core.lib.logs import log
from xio.core.lib.utils import is_string, urlparse, generateuid

from .containers import Containers

import traceback
from pprint import pprint
import datetime
import os.path
import hashlib
import base64
import uuid

import time
import json

import sys
import collections


def node(*args, **kwargs):
    return Node.factory(*args, **kwargs)


class Node(App):

    @classmethod
    def factory(cls, id=None, *args, **kwargs):

        # check network instance
        if id and callable(id):
            # create instance, send args,kwars for config
            about = args[0] if args else None
            node = Node(network=id, about=about)
            return node

        kwargs.setdefault('_cls', cls)
        return App.factory(id, *args, **kwargs)

    def __init__(self, name=None, network=None, **kwargs):

        App.__init__(self, name, **kwargs)

        self.uid = generateuid()

        # if network defined we have to connect to it for AUTH handling
        # to fix ... need to handle node connected to 0x... network or http:/// network
        self.network = self.connect(network) if network else None
        #self.network = network if network else None

        try:
            self._about['network'] = self.network.about()
        except Exception as err:
            self.log.warning('self.network error', err)

        self.bind('www', self.renderWww)

        # service docker
        from .lib.docker.service import DockerService
        self.os.put('services/docker', DockerService(self))

        # service memdb
        import xio
        if self.redis:
            memdb = xio.db(name='xio', type='redis')
        else:
            memdb = xio.db()

        self.os.put('services/db', memdb)

        # fix peers (default python handler)
        from xio.core.peers import Peers
        self.peers = Peers(peer=self, db=memdb)

        # init container (require loaded services)
        self.containers = Containers(self, db=memdb)

        # containers sync
        node_peers_heartbeat = xio.env.get('node_peers_heartbeat', 300)
        self.schedule(node_peers_heartbeat, self.peers.sync)

        # peers sync
        node_containers_heartbeat = xio.env.get('node_containers_heartbeat', 300)
        self.schedule(node_containers_heartbeat, self.containers.sync)

    def start(self, **kwargs):
        """
        if self.network is object we have to start some services (eg dht)
        network = xio.core.handlers.pythonResourceHandler
        """

        App.start(self, **kwargs)

        # self.network.start(self)

        self.containers.sync()
        self.peers.sync()

    def register(self, endpoints):

        if not isinstance(endpoints, list):
            endpoints = [endpoints]

        for endpoint in endpoints:
            return self.peers.register(endpoint)

    def deliver(self, uri):
        return self.containers.deliver(uri)

    def renderWww(self, req):
        """
        options: ABOUT,GET
        """

        # why this line ?
        #req.path = self.path +'/'+ req.path if self.path else req.path

        if req.path == 'favicon.ico':
            return

        self.log.info('NODE.RENDER', req)
        self.log.info(req.headers)

        if req.OPTIONS:
            return ''

        # require ethereum account based authentication
        req.require('auth', 'xio/ethereum')

        # NODE DELIVERY
        if not req.path:

            log.info('==== NODE DELIVERY =====', req.method or req.xmethod, repr(req.path))
            log.info('==== USER =====', req.client.id)

            # handle network resources listings
            if req.GET:

                # node peers
                #peers = [peer.about().content for peer in self.peers.select()]
                # return peers

                resources = []
                print(self.network)
                req.path = 'www'  # bug
                rows = self.network.request(req).content
                for row in rows:
                    appid = row.get('provider')
                    if appid:
                        peer = self.peers.get(appid)
                        print('===== appid', appid, peer)
                        row['available'] = bool(peer)
                    resources.append(rows)
                return resources

            elif req.ABOUT:

                about = self._handleAbout(req)
                about['id'] = self.id  # fix id missing
                if self.network:
                    about['network'] = self.network.about().content
                if req.client.peer:
                    about['user'] = {'id': req.client.peer.id}
                return about
            elif req.CHECK:
                req.require('scope', 'admin')
                return self._handleCheck(req)
            elif req.REGISTER:
                endpoint = req.data.get('endpoint', req.context.get('REMOTE_ADDR').split(':').pop())  # '::ffff:127.0.0.1'
                if not '://' in endpoint:
                    endpoint = 'http://%s' % endpoint
                return self.peers.register(endpoint)
            elif req.CHECKALL:
                return self.checkall()
            elif req.SYNC:
                return self.peers.sync()
            elif req.CLEAR:
                return self.peers.clear()
            elif req.EXPORT:
                return self.peers.export()

             # method not allowed
            raise Exception(405, 'METHOD NOT ALLOWED')

        assert req.path

        p = req.path.split('/')
        peerid = p.pop(0)
        assert peerid

        # forward /user to network
        if peerid == 'user':
            req.path = 'www/' + req.path
            return self.network.request(req)

        log.info('==== DELIVERY REQUEST =====', req.method, req.xmethod)
        log.info('==== DELIVERY FROM =====', req.client.id)
        log.info('==== DELIVERY TO   =====', peerid)

        peer = self.peers.get(peerid)

        # check if peerid is a contract serviceid
        if not peer:

            service = self.network.get('www/%s' % peerid).content

            assert service, Exception(404)
            assert service.get('id') == peerid

            pprint(service)
            serviceid = service.get('id')
            peerid = service.get('provider')
            peer = self.peers.get(peerid)

            # to fix - surity pb
            quotas = self.network.request('GET', 'www/user/subscriptions/%s' % serviceid, headers={'Authorization': req.headers.get('Authorization')}).content

            #quotas = self.network.get('www/user/subscriptions/%s' % serviceid).content

            #self.network.getUserSubscription(req.client.id, serviceid)
            assert quotas, Exception(428)
            assert quotas.get('ttl'), Exception(428)  # check ttl
            #raise Exception(428,'Precondition Required')
            #raise Exception(429,'QUOTA EXCEEDED')

            log.info('==== DELIVERY QUOTAS   =====', quotas)
            import json
            req.headers['XIO-quotas'] = json.dumps(quotas)

            log.info('==== DELIVERY PROVIDER   =====', peerid)
            """    
            # fallback about for peer not registered
            if req.ABOUT and not p and not peer:
                row = self.network.getResource(peerid)
                assert row,404
                return row
            """

        assert peer, Exception(404)

        # checkpoint, handle userid/serviceid registration,stats,quota
        profile = 'basic'
        basestat = (req.client.id, peerid, profile)
        req.require('quota', 1000, basestat)
        userid = req.client.id
        assert userid

        try:
            req.path = '/'.join(p)
            resp = peer.request(req)
            print(peer)
            print(resp)

            req.response.status = resp.status
            req.response.headers = resp.headers  # pb si header transferé tel quel ->
            req.response.content_type = resp.content_type
            req.response.ttl = resp.ttl
            return resp.content
        except Exception as err:
            traceback.print_exc()
            req.response.status = 500

        # NETWORK DELIVERY
        return self.network.render(req)
