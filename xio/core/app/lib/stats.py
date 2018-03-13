#!/usr/bin/env python
#-*- coding: utf-8 -*--

import xio

import json

from pprint import pprint
import copy


"""
    def check(self,req):
        # controle api
        # check quota
        # consolidation des données

            
        user_id = req.user.id
        service_id = self.id
        profile_id = 0 #req.profile.id
        profile_rules = [
            {
                'type': 'requests',
                'limit': 100
            }
        ]

        if user_id and profile_rules:

            log.debug('==== STATS =====', user_id, service_id, profile_id )

            redis = self.resources.node.redis
            dt = datetime.datetime.now().strftime('%y%m%d')  # gestion des quota (daily)

            log.debug('======== PROFILE RULES',profile_rules)

            key = 'inxio:stats:%s:%s:%s' % (dt,user_id,service_id)
            counter = redis.get(key) or 0
            for r in profile_rules: # tofix: recherche requests rule for limit a optimiser
                if r.get('type')=='requests':
                    limit = r.get('limit')
                    log.debug('======== QUOTA %s / %s' % (counter,limit) ) 
                    assert not limit or int(counter)<int(limit), Exception(429,'DAILY QUOTA EXECEDDED !')
            redis.incr(key) 

            # gestion des stats de facturation 
            key = 'inxio.stats:%s:%s:%s:%s' % (dt,req.user.id,service_id,profile_id) 
            redis.incr(key) 
            log.debug('======== TO BILL',key, redis.get(key) )
"""



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





            


