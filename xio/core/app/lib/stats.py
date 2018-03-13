#!/usr/bin/env python
#-*- coding: utf-8 -*--

import xio

import json

from pprint import pprint
import copy


class StatsManager:

    def __init__(self):
        self.db = xio.db(__name__).container('stats')


    def inc(self,index,value):
        self.db.put(index,value)
        

    def get(self,filter=None):
        keys = app.redis.keys('xio:peers:%s:stats:%s:*' % (peerid,date))
        return [ ( key, app.redis.hgetall(key) ) for key in keys ] 

        


if __name__=='__main__':


    import unittest


    manager = StatsManager()

    class Tests(unittest.TestCase):

            
        def test(self):
            print manager.inc('someindex')
            print manager.get('someindex')

    unittest.main()





            


