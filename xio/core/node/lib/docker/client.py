#!/usr/bin/env python
#-*- coding: utf-8 -*--
from __future__ import absolute_import
import sys
import os
from pprint import pprint
import datetime



class Docker:

    def __init__(self):

        import docker
        
        #self.docker = docker.Client(base_url='unix://var/run/docker.sock',version='auto') #1.23
        self.docker = docker.from_env()
        import xio
        self.host = xio.env.get('docker', '127.0.0.1')
        
    def build(self,image=None,directory=None,dockerfile=None,**kwargs):
        """
        # https://docker-py.readthedocs.io/en/stable/images.html
        # https://github.com/docker/docker-py/issues/1400
        from io import BytesIO
        import docker
        dockerfile = 'FROM alpine:3.6'
        f = BytesIO(dockerfile.encode('utf-8'))
        #image = self.docker.images.build(fileobj=f, tag='test/py', nocache=True, rm=True) # rm=True, 

        # alternative avec logs : http://docker-py.readthedocs.io/en/stable/api.html#module-docker.api.build
        """
        from docker import APIClient
        from io import BytesIO

        cli = APIClient(base_url='unix://var/run/docker.sock',version='auto')

        kwargs = dict(
            path=directory,
            rm=True, 
            tag=image, 
            decode=True
        )

        if not dockerfile:
            dockerfile = directory+'/Dockerfile'
            if not os.path.isfile(dockerfile):
                dockerfile = "from inxio/app"

        # 
        filepath = None
        if not "\n" in dockerfile and not " " in dockerfile:
            filepath = directory+'/'+dockerfile if not dockerfile.startswith('/') else dockerfile
            print ('>>>>', filepath)
        if filepath and os.path.isfile(filepath):
            kwargs['dockerfile'] = filepath
        else:
            f = BytesIO(dockerfile.encode('utf-8'))
            kwargs['fileobj'] = f



        # bug IOError: Can not access file in context => https://github.com/docker/docker-py/issues/1841
        for line in cli.build(**kwargs): # squash=True ??? "squash is only supported with experimental mode
            print( line.get('stream','').strip() )
        
        return self.image(name=image)

    def run(self,**info):
        # https://docker-py.readthedocs.io/en/stable/containers.html#
        
        iname = info.get('image')
        cname = info.get('name',iname.replace('/','-'))

        assert iname and cname
        

        env = info.get('env',{})

        ports = {}
        for key,val in info.get('ports',{}).items():
            ports[key] = val
        
        """
        volumes (dict or list) –
        A dictionary to configure volumes mounted inside the container. The key is either the host path or a volume name, and the value is a dictionary with the keys:

        bind The path to mount the volume inside the container
        mode Either rw to mount the volume read/write, or ro to mount it read-only.
        For example:

        {'/home/user1/': {'bind': '/mnt/vol2', 'mode': 'rw'},
         '/var/www': {'bind': '/mnt/vol1', 'mode': 'ro'}}

        """
        volumes = info.get('volumes',{})
        for src,dst in volumes.items():
            volumes[src] = {'bind': dst, 'mode': 'rw'} # 'mode': 'ro'

        # stop and remove previous container
        c = self.container(name=cname)
        if c:
            print ('... stop and remove',cname)
            c.stop()
            c.remove()

        kwargs = dict(name=cname,detach=True,ports=ports,volumes=volumes,environment=env)
        print ('... RUN', iname,cname, kwargs)
        c = self.docker.containers.run(iname,**kwargs)
        cid = c.attrs.get('Id')
        return self.container(id=cid)



    def images(self,pattern=None):
        images = self.docker.images.list(all=True)
        result = []     
        for i in images:
            image = Image(self,i)
            if image.name and ( not pattern or pattern in image.name):
                result.append(image)
        return result                    
              
    def image(self,name=None,id=None):
        images = self.images()
        for image in images:
            if id and image.id==id:
                return image
            #print (name,image.name)
            if name and image.name==name:
                return image

    def containers(self,pattern=None,image=None):
        containers = self.docker.containers.list(all=True)   
        result = []
        for c in containers:
            container = Container(self,c)
            if container.name and ( not pattern or pattern in c.name):
                if not image or image==container.image:
                    result.append(container)
        return result  

    def container(self,name=None,id=None):
        containers = self.containers()
        for container in containers:
            if id and container.id==id:
                return container
            if name and container.name==name:
                return container

  


class Image:

    def __init__(self,docker,image):
        self.docker = docker
        self.image = image
        self.raw = image.attrs
        self.id = image.attrs.get('Id')

        repo = image.attrs.get('RepoTags')
        self.name,self.version = repo[-1].split(':') if repo else ('','')
        self.name = self.name.strip()

        self.size = int(image.attrs.get('Size')/1000000)
        self._about = {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'created': image.attrs.get('Created'),
            'size': self.size,        
        }
        

    def __repr__(self):
        return 'DOCKER IMAGE #%s : %s %s:%s (created %s, size %s Mb)' % (self.id,self.name,self.version,self.version,self._about.get('created'),self._about.get('size'))

    def about(self):
        return self._about

    def containers(self):
        return self.docker.containers(image=self.image.id)




class Container:

    def __init__(self,docker,container):
        self.docker = docker
        self.container = container
        self.raw = container.attrs
        self.name = container.attrs.get('Name')[1:]
        self.id = container.attrs.get('Id')
        #self.image = self.docker.image(id=container.attrs.get('Image'))
        self.image = container.attrs.get('Image')

        info = self.raw
        #created = datetime.datetime.fromtimestamp(info.get('Created')).strftime('%Y-%m-%d %H:%M')  
        http_endpoint = ws_endpoint = None 

        """
        u'Ports': {
            u'80/tcp': None,
            u'81/tcp': [
                {u'HostIp': u'0.0.0.0',
                u'HostPort': u'7501'}
            ],
             u'84/tcp': None
        },
        """
        ports = info.get('NetworkSettings',{}).get('Ports',{})
        self.ports = {}
        for k,v in ports.items():
            if v:
                p = v[0].get('HostPort')
                if p:
                    self.ports[int(p)] = int( k.split('/')[0] )

        self.status = info.get('State').get('Running')==True
        self.running = info.get('State').get('Running')==True
        self._about = {
            'id': self.id,
            'name': self.name,
            'created': info.get('Created'),
            'status': self.status,
            'image': self.image,
            'port': self.ports
        }
        
    def __repr__(self):
        return 'DOCKER CONTAINER #%s : %s (%s)' % (self.id,self.name,self._about.get('status'))

    def about(self):
        return self._about

    def stop(self):
        return self.container.stop()

    def remove(self):
        return self.container.remove()


   
