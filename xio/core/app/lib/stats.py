#!/usr/bin/env python
#-*- coding: utf-8 -*--

import xio

from xio.core.lib.utils import md5

import json

from pprint import pprint
import copy
import datetime

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


class PythonHandler:
    
    def __init__(self):
        self.data = {}

    def get(self,index):
        return self.data.get(index,0)

    def incr(self,index):
        self.data.setdefault(index,0)
        self.data[index]+=1
        return self.data[index]


class RedisHandler:
    
    def __init__(self):
        import redis
        self.redis = redis.Redis()

    def get(self,index):
        key = 'xio:stats:%s' % (':'.join(index))
        counter = self.redis.get(key) 
        return counter or 0

    def incr(self,index):
        key = 'xio:stats:%s' % (':'.join(index))
        counter = self.redis.get(key) or 0
        print counter
        self.redis.incr(key) 
        return counter


__HANDLERS__ =  {
    'python': PythonHandler,
    'redis': RedisHandler,
}


class StatsService:

    def __init__(self,app,type='auto'):

        if type=='auto':
            type = 'redis' if app.redis else 'python'

        self.handler = __HANDLERS__.get(type)()

    def get(self,uid):
        dt1 = datetime.datetime.now().strftime('%y%m%d%H') # hourly
        index1 = (dt1,uid)
        return self.handler.get(index1)

    def incr(self,uid):
        dt1 = datetime.datetime.now().strftime('%y%m%d%H') # hourly
        index1 = (dt1,uid)
        return self.handler.incr(index1)
        """

        dt1 = datetime.datetime.now().strftime('%y%m%d%H') # hourly
        #dt2 = datetime.datetime.now().strftime('%y%m%d') # daily
        #dt2 = datetime.datetime.now().strftime('%y%m') # monthly        
        index1 = md5( path,userid )
        #print 'putStat???', repr(path),userid,index1
        #index2 = (userid,path,dt2)
        #index3 = (userid,path,dt3)

        stats = self.db.get(index1) or {'count': 0, 'path': path, 'userid': userid}
        stats['count'] += 1
        self.db.put(index1,stats)
        return stats['count']
        """



    def __call__(self,req):

        uid = req.path

        if req.GET:
            return self.get(uid)

        if req.INCR:
            return self.incr(uid)

        if req.POST:
            return self.incr(req.data.get('path'),req.data.get('userid'))





            


