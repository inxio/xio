#!/usr/bin/env python
#-*- coding: utf-8 -*--
 
from xio.core import resource
from xio.core.request import Request,Response

from xio.core.app.app import (
    App,
    handleRequest,
    handleCache,
    handleStats,
)

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



def node(*args,**kwargs):
    return Node.factory(*args,**kwargs)


class Node(App):

    @classmethod
    def factory(cls,id=None,*args,**kwargs):

        # check network instance
        if id and callable(id):
            # create instance, send args,kwars for config
            about = args[0] if args else None
            node = Node(network=id,about=about) 
            return node
            
        kwargs.setdefault('_cls',cls)    
        return App.factory(id,*args,**kwargs)
        

    def __init__(self,name=None,network=None,**kwargs):

        App.__init__(self,name,**kwargs)


        self.uid = generateuid()

        # if network defined we have to connect to it for AUTH handling    
        self.network = self.connect(network) if network else None
        
        # SERVER NODE ONLY - this node need to publish stuff to network (dht mainly)
        # networkhandler sync ===> server context only
        try:
            networkhandler = self.network._handler.handler._handler
            #self.dht = networkhandler.dht
        except:
            pass
        self.dht = None

        self.bind('www', self.renderWww)   

        # service docker
        from .lib.docker.service import DockerService
        self.put('services/docker', DockerService(self) )


        # service memdb
        import xio
        print ('create node db', self.redis)
        self.redis = False
        if self.redis:
            memdb = xio.db(name='xio',type='redis')
        else:
            memdb = xio.db()
            
        self.put('services/db', memdb )


        # fix peers (default python handler)
        from xio.core.peers import Peers
        self.peers = Peers( db=memdb )

        # init container (require loaded services)
        self.containers = Containers(self, db=memdb )

        # containers sync
        node_peers_heartbeat = xio.env.get('node_peers_heartbeat',300)
        self.schedule( node_peers_heartbeat, self.containers.sync)

        # peers sync
        node_containers_heartbeat = xio.env.get('node_containers_heartbeat',300)
        self.schedule( node_containers_heartbeat, self.peers.sync)

        # dht sync
        node_dht_heartbeat = xio.env.get('node_dht_heartbeat',300)
        self.schedule( node_dht_heartbeat, self.syncDht )

        

    def start(self,**kwargs):
        """
        if networkhandler is object we have to start some services (eg dht)
        network = xio.core.handlers.pythonResourceHandler
        """    
    
        App.start(self,**kwargs)

        try:
            # if exist this node act as a server
            networkhandler = self.network._handler.handler._handler
        except:
            # maybe remote network, this node is a client
            networkhandler = None 
            
        if networkhandler:
            networkhandler.start(self)
            
        

    def register(self,endpoints):
        
        if not isinstance(endpoints,list):
            endpoints = [endpoints]

        for endpoint in endpoints:
            return self.peers.register(endpoint)


    def deliver(self,uri):
        return self.containers.deliver(uri)


    def syncDht(self):

        if self.dht:
            print ('=============> SYNC DHT',self.dht)

            # declare node 
            self.dht.put('xrn:xio:node', self.id)
            
            # declare apps 
            for peer in self.peers.select(type='app'):
                print (peer)
                self.dht.put(peer.id, self.id)
    
    def renderWww(self,req):

        # why this line ?
        #req.path = self.path +'/'+ req.path if self.path else req.path

        self.log.info('NODE.RENDER',req) 

        if req.OPTIONS:
            return ''

        # NODE DELIVERY
        if not req.path:
            log.info('==== NODE DELIVERY =====', req.path, req.method, req.xmethod )

            if req.GET:
                return [ peer.getInfo() for peer in self.peers.select() ]

            elif req.ABOUT:
                about = self._handleAbout(req)
                if self.network:
                    about['network'] = self.network._handleAbout(req)
                if req.client.peer:
                    about['user'] = req.client.peer._handleAbout(req)
                return about

            elif req.REGISTER:
                endpoint = req.data.get('endpoint', req.context.get('REMOTE_ADDR').split(':').pop() ) #  '::ffff:127.0.0.1' 
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

        
        else:
               
            p = req.path.split('/')
            peerid = p.pop(0)
            assert peerid

            peer = self.peers.get(peerid)
            assert peer,404
            
            log.info('==== DELIVERY REQUEST =====', req.method, req.xmethod )
            log.info('==== DELIVERY FROM =====', req.client.id )
            log.info('==== DELIVERY TO   =====', peerid) 
            try:
                req.path = '/'.join(p)
                resp = peer.request(req)
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



        







