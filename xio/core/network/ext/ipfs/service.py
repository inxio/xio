#!/usr/bin/env python
#-*- coding: utf-8 -*--
from __future__ import absolute_import
from .connector import Connector

def IpfsService(*args,**kwargs):
    return Connector()
"""
class IpfsService:

    def __init__(self,app):
        self.app = app
        self.ipfs = Connector()
        
    def __call__(self,req):
        return 'ipfs ready'


"""
   
