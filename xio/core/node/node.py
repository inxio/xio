#!/usr/bin/env python
#-*- coding: utf-8 -*--
 
from xio.core import resource
from xio.core.lib.request import Request,Response

from xio.core.app.app import App

from xio.core.lib.logs import log
from xio.core.lib.utils import is_string, urlparse, generateuid

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

    def __init__(self,name=None,network=None,**kwargs):

        App.__init__(self,name,**kwargs)

        self.uid = generateuid()
        self.network = network
        self.services = [] # list of APP services to deliver


    @classmethod
    def factory(cls,id=None,*args,**kwargs):

        # check network instance
        if id and callable(id):
            node = Node(network=id)
            return node
                
        return peer.Peer.factory(id,*args,_cls=cls,**kwargs)



    def render(self,req):
        
        req.path = self.path +'/'+ req.path if self.path else req.path
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


        """         
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
            #req.response.ttl = resp.ttl
            return resp.content      
        except Exception as err:
            traceback.print_exc()
            req.response.status = 500
        """

               
        # NETWORK DELIVERY
        return self.network.render(req)



        


    def register(self,endpoints):
        
        if not isinstance(endpoints,list):
            endpoints = [endpoints]

        for endpoint in endpoints:
            return self.peers.register(endpoint)








