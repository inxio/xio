#!/usr/bin/env python
#-*- coding: utf-8 -*--
 
from __future__ import absolute_import, division, print_function, unicode_literals


from xio.core.resource import resource,Resource, handleRequest

from xio.core.lib.request import Request,Response
from xio.core.lib.logs import log

from xio.core.lib.utils import is_string, urlparse, md5
from xio.core.peer import Peer

from xio import db

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

    def __init__(self,peer=None):
        self.id = peer.id if peer else None
        self.db = db('xio:peer:%s' % self.id).container('peers')


    def register(self,endpoint=None,nodeid=None,type=None,uid=None,id=None,name=None):

        assert endpoint
        nodeid = nodeid or self.id
        uid = uid if uid else None
        peertype = type if type else None
        peerid = id if id else None
        peername = name if name else None

        assert endpoint

        if not is_string(endpoint):
        
            
            assert isinstance(endpoint,Peer) or isinstance(endpoint, collections.Callable)   
            if not peertype:   
                peertype = endpoint.__class__.__name__.lower()
                peerid = endpoint.id
                peername = endpoint.name

        import xio
        import copy
        
        log.info('register',endpoint)

        if not peerid:
            client = xio.resource(endpoint)
            resp = client.request('ABOUT') 
            assert resp.status == 200
            peername = resp.content.get('name', None) 
            peerid = resp.content.get('id')
            peertype = resp.content.get('type',peertype).lower()

        assert peerid  
        assert peerid != self.id


        for peer in self.select(id=peerid):
            if peer.data.get('nodeid')==nodeid and peer.id==peerid:
                #print(('register ALREADY EXIST', peerid)) 
                return 

        if not uid:
            uid = md5( '%s/%s' % (nodeid,peerid) )


        data = {
            'uid': uid,
            'nodeid': nodeid,
            'id': peerid,
            'name': peername,
            'endpoint': endpoint,
            'type': peertype.lower(),
            'status': 200
        }
        self.put(uid,data)
        return self.get(uid)


    def unregister(self,peerid):
        for peer in self.select(id=peerid, nodeid=self.id):
            self.delete(peer.uid)



    def get(self,index,**kwargs):

        # lookup by uid
        key = 'xio:peers:%s' % index
        data = self.db.get(key)
        if data:
            peer = PeerClient( **data ) if not isinstance(data,PeerClient) else data
            return peer 

        # lookup by xrn
        if index.startswith('xrn:'):
            rows = self.select(name=index)
            return rows[0] if rows else None 
            
        # lookup by id
        byids = self.select(id=index)
        return byids[0] if byids else None   


            

    def select(self,**filter):
        result = []
        for row in self.db.select(filter=filter):
            result.append( row )
        return [ PeerClient(**row) for row in result ]
        

    def put(self,index,peer):
        key = 'xio:peers:%s' % index
        self.db.put(key,peer)

    def delete(self,index):
        key = 'xio:peers:%s' % index
        self.db.delete(key)


    def export(self):
        result = []
        for peer in self.select():

            if not peer.endpoint:
                continue

            if peer.status not in (200,201): 
                continue

            if peer.type=='app' and not peer.endpoint:
                continue

            if peer.type=='app':
                 mod = PEER_MOD_PROTECTED
            elif peer.type=='node':
                if peer.conn_type=='WS' or not is_string(peer.endpoint):
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
                'endpoint': peer.endpoint if mod==PEER_MOD_PUBLIC else '~/'+peer.uid
            }
             
            result.append(info)
           
        return result


    def check(self,maxage=60):

        for peer in self.select():

            t1 = time.time()
            t0 = peer.checked
            if not t0 or not maxage or (int(t1)-int(t0) > maxage):

                result = peer.check()
                check_status = result.get('status')
                check_time = result.get('time')

                key = 'xio:peers:%s' % peer.peerid 
                self.update(key,{
                    'status': check_status,
                    'time': check_time,
                    'checked': int(time.time()),
                })

                # keep 24h 
                dt = datetime.datetime.now().strftime('%y:%m:%d:%H:%m')  # handle quota (daily)
                key = 'xio:peers:%s:stats:%s' % (peer.peerid,dt)
                self.put(key,{
                    'status': check_status,
                    'time': check_time,
                    '_ttl': 24*60*60,
                })


    def sync(self):

        log.info('=========== SYNCHRONIZE ...')

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


class PeerClient(Resource): 

    def __init__(self,**data):
        self.data = data
        self.id = data.get('id')
        self.name = data.get('name')
        self.endpoint = data.get('endpoint')
        self.status = data.get('status')
        self.type = data.get('type')
        self.uid = data.get('uid')
        self.conn_type = data.get('conn_type')
        Resource.__init__(self) 
        self.status = data.get('status')

    def check(self): 
        
        headers = {
        }
        try:
            t0 = time.time()     
            resp = self.request('HEAD','',headers=headers) 
            t1 = time.time() 
            check_result = {
                'status': resp.status,
                'time': int((t1-t0)*1000)
            }
        except Exception as err:
            traceback.print_exc()
            check_result = {
                'status':-1,
                'error': traceback.format_exc(),
            }
        return check_result

    def getInfo(self):
        return self.data


    @handleRequest
    def request(self,req):

        import xio

        context = req.client.context or {}
        context['xio_id'] = req.client.id if req.client else 0 
        client = xio.resource(self.endpoint,context)
       
        try:
            res = client.request(req.method, req.path, data=req.data,query=req.query,headers=req.headers)
            if res.status==201 and 'Location' in res.headers:
                self.client = xio.resource(res.headers['Location'])

        except Exception as err:
            traceback.print_exc()
            response = Response(-1)
        return res





