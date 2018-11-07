#!/usr/bin/env python
#-*- coding: utf-8 -*--

from __future__ import absolute_import, division, print_function, unicode_literals


from xio.core.resource import resource, Resource, handleRequest
from xio.core.request import Request, Response

from xio.core.lib.logs import log

from xio.core.lib.utils import is_string, urlparse, md5
from xio.core.peer import Peer

import xio

import traceback
from pprint import pprint
import datetime

import hashlib
import base64
import uuid

import time
import json

import sys
import collections

PEER_STATUS_NEW = 0
PEER_STATUS_READY = 1
PEER_STATUS_ERROR = 2

PEER_MOD_PUBLIC = 'public'          # enpoint could be forwarded to other node for direct call
PEER_MOD_PROTECTED = 'protected'    # use nodes as gateway
PEER_MOD_PRIVATE = 'private'        # private use for node or other localhost apps


class Peers:

    def __init__(self, peer=None, db=None):
        self.peer = peer
        self.id = peer.id if peer else None
        db = db or xio.db()
        self.db = db.container('peers')
        self.db.truncate()
        # db for instances
        self.localresources = xio.db().container('resources')

    def register(self, endpoint=None, nodeid=None, type=None, uid=None, id=None, name=None, sub_register=False):

        assert endpoint
        nodeid = nodeid or self.id
        uid = uid if uid else None
        peertype = type if type else None
        peerid = id if id else None
        peername = name if name else None

        assert endpoint
        assert is_string(endpoint) or isinstance(endpoint, Peer) or isinstance(endpoint, collections.Callable)

        log.info('register', endpoint, 'by', self.peer)

        client = xio.client(endpoint, client=self.peer)
        resp = client.about()
        about = resp.content
        assert about

        peerid = about.get('id')
        peername = about.get('name', None)

        # fix pb peerid missing for sub-services
        if sub_register:
            peername = sub_register  # fix for child xrn missing
            assert peerid

        peertype = about.get('type', 'app').lower()

        assert peerid
        assert peerid != self.id

        # handle provides (multi services)
        # tofix: move this feature to node.peers
        if not sub_register:

            provide = resp.content.get('provide')
            if provide:
                for xrn in provide:
                    try:
                        # check sub xrn name
                        assert xrn.startswith(peername + ':'), Exception('invalid xrn')
                        postpath = xrn.split(':').pop()
                        if not is_string(endpoint):
                            childendpoint = client.get(postpath)
                        else:
                            childendpoint = endpoint + '/' + postpath
                        self.register(childendpoint, sub_register=xrn)
                    except Exception as err:
                        log.error('subregister', xrn, err)
                        #import traceback
                        # traceback.print_exc()

            # let registering container base (for admin scope only ?)

        for peer in self.select(id=peerid):
            if peer.data.get('nodeid') == nodeid and peer.id == peerid:
                log.warning('register ALREADY EXIST', peerid)
                return

        if not uid:
            uid = md5(nodeid, peerid)

        # handle local resources for external db (eg redis)
        if not is_string(endpoint):
            self.localresources.put(uid, {'endpoint': endpoint})
            endpoint = '~'

        data = {
            'uid': uid,
            'nodeid': nodeid,
            'id': peerid,
            'name': peername,
            'endpoint': endpoint,
            'type': peertype.lower(),
            'status': 200
        }
        self.put(uid, data)
        return self.get(uid)

    def unregister(self, peerid):
        for peer in self.select(id=peerid, nodeid=self.id):
            self.delete(peer.uid)

    def get(self, index, **kwargs):

        # lookup by uid
        data = self.db.get(index)
        if data:
            peer = PeerClient(self, **data) if not isinstance(data, PeerClient) else data
            return peer

        # lookup by xrn
        if str(index).startswith('xrn:'):
            rows = self.select(name=index)
            return rows[0] if rows else None

        # lookup by id
        byids = self.select(id=index)
        return byids[0] if byids else None

    def select(self, **filter):
        result = []
        for row in self.db.select(filter=filter):
            result.append(row)
        return [PeerClient(self, **row) for row in result]

    def put(self, index, peer):
        self.db.put(index, peer)

    def delete(self, index):
        self.db.delete(index)

    def export(self):
        result = []
        for peer in self.select():

            if not peer.endpoint:
                continue

            if peer.status not in (200, 201):
                continue

            if peer.type == 'app' and not peer.endpoint:
                continue

            if peer.type == 'app':
                mod = PEER_MOD_PROTECTED
            elif peer.type == 'node':
                if peer.conn_type == 'WS' or not is_string(peer.endpoint):
                    mod = PEER_MOD_PROTECTED
                else:
                    mod = PEER_MOD_PUBLIC
            else:
                mod = PEER_MOD_PUBLIC

            info = {
                'type': peer.type,
                'uid': peer.uid,
                'name': peer.name,
                'id': peer.id,
                'endpoint': peer.endpoint if mod == PEER_MOD_PUBLIC else '~/' + peer.uid
            }

            result.append(info)

        return result

    def sync(self):

        log.info('=========== PEERS SYNCHRONIZE ...')

        # check all peers

        maxage = 60

        for peer in self.select():

            t1 = time.time()
            t0 = peer.checked
            if not t0 or not maxage or (int(t1) - int(t0) > maxage):

                result = peer.check()
                check_status = result.get('status')
                check_time = result.get('time')

                # be carefull with id _id uid => db use _id
                index = peer.data['_id']
                self.db.update(index, {
                    'status': check_status,
                    'time': check_time,
                    'checked': int(time.time()),
                })
                """
                # keep 24h 
                dt = datetime.datetime.now().strftime('%y:%m:%d:%H:%m')  # handle quota (daily)
                key = 'xio:peers:%s:stats:%s' % (peer.peerid,dt)
                self.put(key,{
                    'status': check_status,
                    'time': check_time,
                    '_ttl': 24*60*60,
                })
                """

        """
        # import peers from other node

        for peer in self.select(type='node'):

            try:
                log.info('=========== IMPORT peers FROM ...',peer)
                
                resp = peer.request('EXPORT','')
                rows = resp.content
                for row in rows:
                    try:
                        
                        endpoint = row['endpoint']
                        if endpoint.startswith('~'):

                            if is_string(peer.endpoint):

                                endpoint = endpoint.replace('~',peer.endpoint) 
                            else:
                                # assuming that endpoint is a Resource (node,app,user)
                                enpoint_basepath = endpoint.replace('~/','')   
                                node = peer.endpoint
                                import xio
                                endpoint = xio.resource(node).get(enpoint_basepath)  
                                assert endpoint.about().content.get('id')==row['id']

                            row['endpoint'] = endpoint    
     
                        self.register(nodeid=peer.id,**row)
                    except Exception as err:
                        log.warning('sync peer ERROR', err ) 
                        traceback.print_exc()

            except Exception as err:
                log.warning('sync node ERROR', err ) 
                traceback.print_exc()

        """


class PeerClient(Resource):

    def __init__(self, peers, **data):
        self.peers = peers
        self.data = data
        self.id = data.get('id')
        self.name = data.get('name')
        self.endpoint = data.get('endpoint')
        self.status = data.get('status')
        self.type = data.get('type')
        self.uid = data.get('uid')
        self.checked = int(data.get('checked', 0))
        self.conn_type = data.get('conn_type')
        Resource.__init__(self)
        self.status = data.get('status')

    def check(self):

        headers = {
        }
        try:
            t0 = time.time()
            resp = self.request('HEAD', '', headers=headers)
            t1 = time.time()
            check_result = {
                'status': resp.status,
                'time': int((t1 - t0) * 1000)
            }
        except Exception as err:
            traceback.print_exc()
            check_result = {
                'status': -1,
                'error': traceback.format_exc(),
            }
        return check_result

    def getInfo(self):
        return self.data

    @handleRequest
    def request(self, req):

        import xio

        context = req.client.context or {}
        if self.endpoint == '~':
            # get client instance from local storage
            endpoint = self.peers.localresources.get(self.uid).get('endpoint')
        else:
            endpoint = self.endpoint

        client = xio.client(endpoint, context)

        try:
            res = client.request(req.method, req.path, data=req.data, query=req.query, headers=req.headers)
            if res.status == 201 and 'Location' in res.headers:
                self.client = xio.client(res.headers['Location'])

        except Exception as err:
            traceback.print_exc()
            response = Response(-1)
        return res
