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

    def __init__(self,node):
    
        self.node = node

        # warning, services may be unavalable yet (required full app/init or app/start)
        
        self.docker = node.service('docker').content  # skip resource wrapper
        self.ipfs = node.service('ipfs')
        
        self.db = node.service('db').container('peers') # , factory=Container => pb for Containers arg 

        
    def get(self,index):
        container = Container(self,index,container=self.db)
        return container


    def deliver(self,uri):

        index = md5(uri)
        container = self.get(index)
        if not container._created:
            container.uri = uri    
            container.save()


    def sync(self):

        from pprint import pprint
        
        # fetch container to provide
        res = self.node.network.getContainersToProvide(self.node.id)
        for row in res:
            self.deliver(row)


        # sync deliverable containers
        for row in self.db.select():
            container = self.get(row['_id'])
            container.sync()




    def oldsync(self):

        running_endpoints = []
        for container in self.docker.containers():
            name = container.data['name']
            http_endpoint = container.data['endpoints'].get('http')
            if http_endpoint:
                running_endpoints.append(http_endpoint)

        for endpoint in running_endpoints:
            try:
                print ('*** register docker container', endpoint)
                self.node.peers.register( endpoint )
            except Exception as err:
                #import traceback
                #traceback.print_exc()
                print ('dockersync error',err) 
        """        
        print '=== peers'
        for peer in node.peers.select():
            if peer.endpoint and '127.0.0.1' in peer.endpoint:
                print peer.name, peer.endpoint
        """

    def select(self):
        return self.docker.containers('xio')   
        

    def images(self):
        return self.docker.images('xio') 
            

    """
    running_endpoints = []
    for container in containers:
        name = container.get('Names')[0]
        running = bool(container.get('State'))
        if 'inxio' in name:
            from pprint import pprint 
            #pprint(container)

            for p in container.get('Ports'):
                if p.get('PrivatePort')==8080:
                    port = p.get('PublicPort')
                    #print '*****', name, running,port
                    running_endpoints.append('http://127.0.0.1:%s' % port)
                elif p.get('PrivatePort')==8484:
                    port = p.get('PublicPort')
                    #print '*****', name, running,port
                    running_endpoints.append('ws://127.0.0.1:%s' % port)

    print '*** running_endpoints', running_endpoints

    for peer in node.peers.select():
        if not peer.endpoint:
            running_endpoints.remove(peer.endpoint)
        elif '127.0.0.1' in peer.endpoint: 
            try:
                if peer.endpoint not in running_endpoints:
                    print '*** remove', peer.endpoint
                    node.peers.unregister( peer.peerid )
                else:
                    running_endpoints.remove(peer.endpoint)
            except Exception,err:
                print 'dockersync error',err    

    for endpoint in running_endpoints:
        try:
            print '*** add', endpoint
            node.peers.register( endpoint )
        except Exception,err:
            #import traceback
            #traceback.print_exc()
            print 'dockersync error',err    
        """



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


    def sync(self):

        # build it if not builded
        if not self.builded:
            self.build()

        if not self.started:
            self.start()
            if self.started and self.endpoint:
                self._containers.node.register(self.endpoint)
       

    def build(self):

        print ('building ...', self.id)

        if self.uri.startswith('/'):
            self.directory = self.uri

        about_filepath = self.directory+'/about.yml'
        with open(about_filepath) as f:
            data = yaml.load(f)

        self.name = data.get('name')
        nfo = self.name.split(':')
        nfo.pop(0)  # strip xrn:

        self.iname = '/'.join(nfo)
        self.cname = self.iname.replace('/','-')

        self._docker.build(name=self.iname,directory=self.directory) # ,dockerfile=self.dockerfile
        self._dockerimage = self._docker.image(name=self.iname)

        assert self._dockerimage

        self.builded = int(time.time())
        self.save()


    def start(self):

        print ('starting ...', self.id)

        cport = 80

        info = {
            'name': self.cname,
            'image': self.iname,
            'ports': {
                0: cport,
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


        pprint(self)

        self.save()







class oldContainer:

    def __init__(self,containers,directory=None,dockerfile=None,data=None):

        self.containers = containers
        self.docker = containers.docker # skip resource wrapper
        self.directory = directory
        self.dockerfile = dockerfile
        
        if not data:
            about_filepath = directory+'/about.yml'
            with open(about_filepath) as f:
                data = yaml.load(f)

        self.data = data

        self.name = data.get('name')
        nfo = self.name.split(':')
        nfo.pop(0)  # strip xrn:

        self.iname = '/'.join(nfo)
        self.cname = self.iname.replace('/','-')

        self.image = self.docker.image(name=self.iname)
        self.container = self.docker.container(name=self.cname)
        self.endpoint = None



    def __repr__(self):
        return 'CONTAINER %s %s' % (self.iname, self.cname)

    def start(self):
        print('STARTING SERVICE',self.name)
        if not self.container:
            self.run()

    def about(self):
        about = self.data
        about.update({
            'image': self.image.about() if self.image else {'name': self.iname},
            'container': self.container.about() if self.container else {'name': self.cname},
        })
        return about


    def build(self):
        #https://docker-py.readthedocs.io/en/stable/images.html

        self.docker.build(name=self.iname,directory=self.directory,dockerfile=self.dockerfile)
        
        self.image = self.docker.image(name=self.iname)
        assert self.image
        return self.image

    def run(self):

        cport = 80

        info = {
            'name': self.cname,
            'image': self.iname,
            'ports': {
                0: cport,
            },
            'volumes': {
                '/apps/xio': '/apps/xio',
                self.directory: '/apps/app',
            }
        }
        self.container = self.docker.run(**info)

        portmapping = self.about().get('container').get('port') # receive {32776: 8080}
        for k,v in portmapping.items():
            if v==cport:
                self.endpoint = 'http://127.0.0.1:%s' % k






    



   
