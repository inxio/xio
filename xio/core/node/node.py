#!/usr/bin/env python
#-*- coding: utf-8 -*--
 
from xio.core import resource
from xio.core.lib.request import Request,Response

from xio.core.app.app import App

from xio.core.lib.logs import log
from xio.core.lib.utils import is_string, urlparse, generateuid

from .peers import Peers

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

    def __init__(self,name=None,**kwargs):

        App.__init__(self,name,**kwargs)

        self.uid = generateuid()
        self.peers = Peers(self)
        self.services = [] # list of APP services to deliver



    def render(self,req):
        
        req.path = self.path +'/'+ req.path if self.path else req.path
        self.log.info('NODE.RENDER',req) 

        if req.OPTIONS:
            return ''

        # NODE DELIVERY
        if not req.path:
            log.info('==== NODE DELIVERY =====', req.path, req.method, req.xmethod )

            if req.GET:
                return [ peer.getInfo() for peer in self.network.peers.select() ]

            elif req.ABOUT:
                return self._handleAbout(req)

            elif req.REGISTER:
                endpoint = req.data.get('endpoint', req.context.get('REMOTE_ADDR').split(':').pop() ) #  '::ffff:127.0.0.1' 
                if not '://' in endpoint:
                    endpoint = 'http://%s' % endpoint
                return self.network.peers.register(endpoint)
            elif req.CHECKALL:
                return self.checkall()  
            elif req.SYNC:
                return self.network.peers.sync()   
            elif req.CLEAR:
                return self.network.peers.clear()
            elif req.EXPORT:
                return self.network.peers.export()

        assert req.path        
        # NETWORK DELIVERY (service / app / user / asset)
        return self.network.request(req,skipnode=True)


    def register(self,endpoints):
        
        if not isinstance(endpoints,list):
            endpoints = [endpoints]

        for endpoint in endpoints:
            return self.network.peers.register(endpoint)








