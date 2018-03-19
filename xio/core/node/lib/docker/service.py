#!/usr/bin/env python
#-*- coding: utf-8 -*--
from __future__ import absolute_import
from .client import Docker


def DockerService(*args,**kwargs):
    return Docker()

"""
class DockerService:

    def __init__(self,app):
        self.app = app
        self.docker = Docker()
        
"""