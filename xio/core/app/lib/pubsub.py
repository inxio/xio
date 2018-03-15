#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
3 handlers possible
    dict
    redis
    zeromq
"""

import xio


class PythonHandler:
    
    def __init__(self):
        self._topics = {}

    def publish(self,topic,message):
        for subscriber in self._topics.get(topic,[]):
            try:
                subscriber(message)   
            except:
                pass 


    def subscribe(self,topic,callback):
        self._topics.setdefault(topic,[])
        self._topics[topic].append(callback)


__HANDLERS__ =  {
    'python': PythonHandler,
}


class PubSubService:
    
    def __init__(self,app,handler='python'):
        cls = __HANDLERS__.get(handler)
        self.handler = cls()

    def publish(self,topic,message):
        return self.handler.publish(topic,message)


    def subscribe(self,topic,callback):
        return self.handler.subscribe(topic,callback)



######################## dev REDIS





### old version

"""

import redis

import json


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


"""

        

            

