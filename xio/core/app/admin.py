#!/usr/bin/env python
#-*- coding: utf-8 -*--


def enhance(app):

    @app.bind('www/xio/admin/about')
    def _(req):
        return app._about

    @app.bind('www/xio/admin/info')
    def _(req):
        import xio
        from threading import current_thread

        key = req.query.get('key')
        if key:
            return key

        result = {
            'req': req._debug(),
        }
        # check env
        import os
        envos = dict()
        for k, v in os.environ.items():
            envos[k] = v

        result['env'] = {
            'thread': current_thread(),
            'os': envos,
            'xio': xio.context,
            'req.context': req.context
        }

        # check redis
        result['redis'] = app.redis
        return result

    @app.bind('www/xio/admin/services')
    def _(req):
        import copy
        services = copy.deepcopy(app._about.get('services', {}))
        for conf in services:
            name = conf.get('name')
            conf.update({
                'client': app.os.get('services').get(name)
            })

        return services

    @app.bind('www/xio/admin/services/:name')
    def _(req):
        name = req.context.get(':name')
        service = app.os.get('services').get(name)
        return service.request(req)

    @app.bind('www/xio/admin/peers')
    def _(req):
        for peer in app.peers.select():
            row = peer.data
            row['@id'] = peer.uid
            yield row

    @app.bind('www/xio/admin/peers/:id')
    def _(req):
        """
        options: ABOUT,GET  
        """
        # need to force ABOUT

        print('===============', req)
        peerid = req.context.get(':id')
        peer = app.peers.get(peerid)

        assert peer
        print(peer)
        method = req.xmethod or req.method
        return peer.request(method, req.path, req.input)

    @app.bind('www/xio/admin/redis')
    def _(req):
        import redis
        r = redis.StrictRedis('localhost')
        for key in r.keys():
            row = {
                '@id': key
            }
            yield row

    @app.bind('www/xio/admin/stats')
    def _(req):
        service = app.service('stats')
        return service.select()
