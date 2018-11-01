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

    def get(self, dt, *args):
        key = 'xio:stats:%s:%s' % (dt, ':'.join(args))
        return self.data.get(key, 0)

    def incr(self, dt, *args):
        key = 'xio:stats:%s:%s' % (dt, ':'.join(args))
        self.data.setdefault(key, 0)
        self.data[key] += 1
        return self.data[key]

    def select(self):
        return [{
            '@id': key,
            'counter': val
        } for key, val in self.data.items()]


class RedisHandler:

    def __init__(self):
        import redis
        self.redis = redis.Redis()

    def get(self, dt, *args):
        key = 'xio:stats:%s:%s' % (dt, ':'.join(args))
        counter = self.redis.get(key)
        return counter or 0

    def incr(self, dt, *args):
        key = 'xio:stats:%s:%s' % (dt, ':'.join(args))
        counter = self.redis.get(key) or 0
        self.redis.incr(key)
        return counter

    def select(self):
        return self.redis.keys('xio:stats')

__HANDLERS__ = {
    'python': PythonHandler,
    'redis': RedisHandler,
}


class StatsService:

    def __init__(self, app, type='auto'):

        if type == 'auto':
            type = 'redis' if app.redis else 'python'

        self.handler = __HANDLERS__.get(type)()

    def select(self):
        return self.handler.select()

    def incr(self, path):
        p = path.split('/')
        dt1 = datetime.datetime.now().strftime('%y%m%d%H')  # hourly
        dt2 = datetime.datetime.now().strftime('%y%m%d')  # daily
        dt3 = datetime.datetime.now().strftime('%y%m')  # monthly
        self.handler.incr(dt1, *p)
        self.handler.incr(dt2, *p)
        self.handler.incr(dt3, *p)
        return True

    def get(self, path):
        p = path.split('/')
        dt1 = datetime.datetime.now().strftime('%y%m%d%H')  # hourly
        dt2 = datetime.datetime.now().strftime('%y%m%d')  # daily
        dt3 = datetime.datetime.now().strftime('%y%m')  # monthly
        v1 = self.handler.get(dt1, *p)
        v2 = self.handler.get(dt2, *p)
        v3 = self.handler.get(dt3, *p)
        return {
            'hourly': v1,
            'daily': v2,
            'monthly': v3,
        }

    def __call__(self, req):

        if req.GET:
            return self.get(req.path)

        if req.INCR:
            return self.incr(req.path)

        if req.SELECT:
            return self.select()
