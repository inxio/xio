#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
3 handlers possible
    dict
    redis
    zeromq
"""

import xio


class EventsService:
    
    def __init__(self,app,config=None):
        self._topics = {}

    def publish(self,topic,message):
        print 'PUBLISH !',topic,message


    def subscribe(self,topic,callback):
        self._topics.setdefault(topic,[])
        self._topics[topic].append(callback)



######################## dev REDIS


import redis

import json



##################### gestion pubsub
import threading
class Listener(threading.Thread):
    def __init__(self, r, topic):
        threading.Thread.__init__(self)
        self.redis = r
        self.topic = topic
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(topic)
        self.callbacks = []
    
    def run(self):
        for item in self.pubsub.listen():
            topic = item['channel']
            data = item['data']
            if data == "unsubscribe":
                self.pubsub.unsubscribe()
                print self, "unsubscribed and finished"
                break
            else:
                for callback in self.callbacks:
                    callback(data)


### old version
"""
class PubsubHandler:        

    def __init__(self):
        self._spool = []
        self.redis = redis.Redis()
        self._listeners = {}

    def publish(self,topic,msg):
        print 'redis publish', topic,msg
        msg = str(msg)
        self.redis.publish(topic,msg)

    def subscribe(self,topic,callback):
        print 'subscribe', topic,callback
        if not topic in self._listeners:
            listener = Listener(self.redis,topic)
            listener.daemon = True
            listener.start()
            self._listeners[topic] = listener
        self._listeners[topic].callbacks.append(callback)
"""



######################## dev ZEROMQ

from xio.tools import process,thread

class PubSubServiceHandlerZeroMq:
    
    def __init__(self,config=None):
        self.config = config or {}
        print 'init PubSubService' # handler par defaut via 
        self._topics = {}

    def publish(self,topic,*args,**kwargs): 
        print 'PUBLISH', topic,args,kwargs
        for callback in self._topics.get(topic,[]):
            callback(*args,**kwargs)   


    def subscribe(self,topic,callback):
        #self._topics.setdefault(topic,[])
        #self._topics[topic].append(callback)

        import zmq

        try:
            endpoint = xio.env('endpoint') 
            if endpoint:
                from urlparse import urlparse
                o = urlparse(endpoint)
                host = o.netloc.split(':').pop(0)
        except Exception,err:
            print 'no endpoint for subscribe !!', err
            host = '127.0.0.1'

        #host = '137.74.172.127'

        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect('tcp://%s:7511' % host) # connect to sub endpoint
        socket.setsockopt(zmq.SUBSCRIBE, "")
        print '>>>> listening', host     
        while True:
            string = socket.recv()  
            print '>>', host,'listener received !!!', string

        

            

