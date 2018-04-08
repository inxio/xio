#!/usr/bin/env python
#-*- coding: utf-8 -*--

import sys
import os
from pprint import pprint
import datetime
import yaml
import time

import xio 

from xio.core.lib.utils import md5

from xio.core.lib.db import db


class Containers:

    def __init__(self,node,db=None):
    
        self.node = node

        # warning, services may be unavalable yet (required full app/init or app/start)
        
        self.docker = node.service('docker').content  # skip resource wrapper

        
        self.ipfs = node.service('ipfs') # pb ipfs is under network.ipfs (not a os.service)
        db = db or xio.db()
        self.db = db.container('containers') # , factory=Container => pb for Containers arg 

        
    def get(self,index):
        container = Container(self,index,container=self.db)
        return container


    def deliver(self,uri):

        index = md5(uri)
        container = self.get(index)
        if not container._created:
            container.uri = uri    
            container.save()

    #@xio.tools.cache(200)        
    def resync(self):
        """ update containers states from current dockers running containers"""
        # sync docker containers
        print ('*** resync from docker container')
        running_endpoints = {}
        for container in self.docker.containers():
            name = container.name
            # find port 8080
            for k,v in container.ports.items():
                if v == 8080:
                    # look like deliverable container
                    http_endpoint = 'http://127.0.0.1:%s' % k

                    running_endpoints[name] = {
                        'endpoint': http_endpoint
                    }
                    
                    try:
                        print('REGISTER',http_endpoint) 
                        #self.node.register( http_endpoint )
                    except Exception as err:
                        #import traceback
                        #traceback.print_exc()
                        print ('dockersync error',err) 
                        
        return running_endpoints


    def sync(self):

        running_endpoints = self.resync()

        
        # fetch container to provide
        try:
            res = self.node.network.getContainersToProvide(self.node.id)
            if res.content:
                for row in res.content:
                    self.deliver(row)
        except Exception as err:
            self.node.log.error('unable to fetch containers to provide',err)


        # sync deliverable containers
        for row in self.db.select():
            container = self.get(row['_id'])
            try:
                container.sync(running_endpoints)
            except Exception as err:
                self.node.log.error('container.sync error',err)



    def select(self):
        return self.db.select()  
        

    def images(self):
        return self.docker.images('xio') 
            




class Container(db.Item):

    def __init__(self,containers,*args,**kwargs):

        self._containers = containers
        self._docker = containers.docker # skip resource wrapper

        db.Item.__init__(self,*args,**kwargs)


    def about(self):
        about = self.data
        about.update({
            'image': self.image.about() if self.image else {'name': self.iname},
            'container': self.container.about() if self.container else {'name': self.cname},
        })
        return about


    def sync(self,running_endpoints=None):

        
        if not self.fetched:
            self.fetch()

        if not self.builded:
            self.build()

        if not self.started:

            running_endpoints = running_endpoints or self._containers.resync()
            if self.cname in running_endpoints:
                self.started = int(time.time()) # to fix, retreive date from docker ps
                self.endpoint = running_endpoints.get(self.cname).get('endpoint')
                self.save()
            else:    
                self.start()

            if self.started and self.endpoint:
                try:
                    self._containers.node.register(self.endpoint)
                except Exception as err:
                    self._containers.node.log.error('unable to register containers endpoint',err)

    def fetch(self):

        print ('fetching ...', self.id,self.uri)

        if self.uri.startswith('/'):
            self.directory = self.uri

        about_filepath = self.directory+'/about.yml'
        with open(about_filepath) as f:
            data = yaml.load(f)

        self.name = data.get('name')
        nfo = self.name.split(':')
        nfo.pop(0)  # strip xrn:

        self.cname = '-'.join(nfo)

        # set image
        dockerfile = self.directory+'/Dockerfile'
        if not os.path.isfile(dockerfile):
            self.iname = 'inxio/app'
            self.dockerfile = None
        else:
            self.iname = self.cname.replace('-','/') 
            self.dockerfile = dockerfile

        self.fetched = int(time.time())
        self.save()


    def build(self):

        print ('building ...', self.id)

        if self.dockerfile:
            self._docker.build(name=self.iname,directory=self.directory) # ,dockerfile=self.dockerfile
            self._dockerimage = self._docker.image(name=self.iname)

        self.builded = int(time.time())
        self.save()


    def start(self):

        print ('starting ...', self.id)
        cport = 80
        info = {
            'name': self.cname,
            'image': self.iname,
            'ports': {
                cport: 0,
                8080: 0, # test/debug
            },
            'volumes': {
                '/apps/xio': '/apps/xio',
                self.directory: '/apps/app',
            }
        }
        self._dockercontainer = self._docker.run(**info)

        assert self._dockercontainer

        portmapping = self._dockercontainer.about().get('port') # receive {32776: 8080}
        for k,v in portmapping.items():
            if v==cport:
                self.endpoint = 'http://127.0.0.1:%s' % k

        self.started = int(time.time())

        self.save()

    def request(self,method,path,query):
        """ test for ihm admin only ?"""
        if self.endpoint:
            import xio

            print(self.endpoint,method,path,query)
            cli = xio.client(self.endpoint)
            print (cli)
            resp = cli.request(method,path,{}) 
            print(resp.content)
            return resp.content
    






