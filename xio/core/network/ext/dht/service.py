#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import absolute_import

import threading
import time
import sys
import logging 


try:
    assert sys.version_info.major > 2
               
    import asyncio
    
    from kademlia.network import Server

    
except:
    print ('DHT REQUIRE PYTHON3')
    pass 



class DhtService:

    def __init__(self,app=None,port=None,bootstrap=None,**kwargs):
        self.app = app
        self.port = 7501 if port==None else port
        self.bootstrap = bootstrap or ('127.0.0.1', 7501)
        self.dhtd = Dhtd(self,self.port,self.bootstrap)
        self.loop = asyncio.new_event_loop()
        
    def start(self):
        self.dhtd.start()

    def stop(self):
        self.dhtd.stop()

    def getKey(self,key):
       
        result = self.loop.run_until_complete( self.dhtd.server.get(key) )
        return result

    def setKey(self,key,value):

        return self.loop.run_until_complete( self.dhtd.server.set(key, value) )


class Dhtd(threading.Thread):

    def __init__(self,h,port,bootstrap):
        threading.Thread.__init__(self)
        self.daemon = True
        self.h = h
        self.port = port
        self.bootstrap = bootstrap
        self.target = self.run
        self.loop = None
        self.server = None
        
    def start(self):
        threading.Thread.start(self) # RuntimeError: There is no current event loop in thread 'Thread-1'.
        #self.run()


    def run(self):

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        log = logging.getLogger('kademlia')
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)


        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        print ('----', asyncio.get_event_loop() )
        
        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(True)

        self.server = Server()
        self.server.listen(self.port)

        self.loop.run_until_complete(
            self.server.bootstrap([self.bootstrap])
        )
        self.loop.run_until_complete(self.server.set('mykey', 'myval'))
        #print (loop.run_until_complete(self.server.get('mykey')))
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.server.stop()
            self.loop.close()

    def stop(self):
        self.server.stop()
        self.loop.close()


if __name__=='__main__':

    dht = DhtService()
    print(dht)
    dht.start()

    dht = DhtService(port=0)
    print(dht)
    dht.start()



    while True:
        pass






