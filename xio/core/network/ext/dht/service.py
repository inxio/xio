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
    print('DHT REQUIRE PYTHON3')
    pass

DEFAULT_PORT = 7500


class DhtService:

    def __init__(self, app=None, port=None, bootstrap=None, **kwargs):
        self.app = app
        self.port = DEFAULT_PORT if port == None else port
        if bootstrap:
            nfo = bootstrap.split(':')
            host = nfo.pop(0)
            port = nfo.pop(0) if nfo else self.port
            bootstrap = (host, port)
        self.bootstrap = bootstrap if bootstrap else ('127.0.0.1', DEFAULT_PORT)
        self.dhtd = Dhtd(self, self.port, self.bootstrap)
        self.loop = asyncio.new_event_loop()

    def about(self):
        return {
            'bootstrap': self.bootstrap,
            'server': self.dhtd.server,
            'debug': self.dhtd.server.storage
        }

    def start(self):
        self.dhtd.start()

    def stop(self):
        self.dhtd.stop()

    def get(self, *args, **kwargs):
        return self.getKey(*args, **kwargs)

    def getKey(self, key):
        # to remove -> use get
        result = self.loop.run_until_complete(self.dhtd.server.get(key))
        return result

    def put(self, *args, **kwargs):
        return self.setKey(*args, **kwargs)

    def setKey(self, key, value):
        print('DHT PUT', key, value)
        # to remove -> use put and/or append
        return self.loop.run_until_complete(self.dhtd.server.set(key, value))

    def getNodes(self, key):

        import random
        import pickle
        import asyncio
        import logging

        from kademlia.protocol import KademliaProtocol
        from kademlia.utils import digest
        from kademlia.storage import ForgetfulStorage
        from kademlia.node import Node
        from kademlia.crawling import ValueSpiderCrawl
        from kademlia.crawling import NodeSpiderCrawl
        from kademlia.network import log

        server = self.dhtd.server

        log.info("Looking up Nodes for Key %s", key)
        dkey = digest(key)

        node = Node(dkey)
        nearest = server.protocol.router.findNeighbors(node)
        if len(nearest) == 0:
            log.warning("There are no known neighbors to get key %s", key)
            return None
        spider = NodeSpiderCrawl(server.protocol, node, nearest,
                                 server.ksize, server.alpha)
        return self.loop.run_until_complete(spider.find())


class Dhtd(threading.Thread):

    def __init__(self, h, port, bootstrap):
        threading.Thread.__init__(self)
        self.daemon = True
        self.h = h
        self.port = port
        self.bootstrap = bootstrap
        self.target = self.run
        self.loop = None
        self.server = None
        self.running = False

    def start(self):
        if not self.is_alive():  # threads can only be started once
            threading.Thread.start(self)  # RuntimeError: There is no current event loop in thread 'Thread-1'.
            # self.run()

    def run(self):

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        log = logging.getLogger('kademlia')
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        print('----', asyncio.get_event_loop())

        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(True)

        self.server = Server()
        self.server.listen(self.port)

        self.loop.run_until_complete(
            self.server.bootstrap([self.bootstrap])
        )
        self.loop.run_until_complete(self.server.set('mykey', 'myval'))
        self.loop.run_until_complete(self.server.set('mykey-%s' % self.port, 'port %s' % self.port))
        #print (loop.run_until_complete(self.server.get('mykey')))
        self.running = True
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            self.server.stop()
            self.loop.close()

    def stop(self):
        self.server.stop()
        self.loop.close()


if __name__ == '__main__':

    dht = DhtService()
    print(dht)
    dht.start()

    dht = DhtService(port=0)
    print(dht)
    dht.start()

    while True:
        pass
