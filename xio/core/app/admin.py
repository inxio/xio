#!/usr/bin/env python
#-*- coding: utf-8 -*--


def enhance(app):

    @app.bind('www/xio/admin/about')
    def _(req):
        return app._about

    @app.bind('www/xio/admin/debug')
    def _(req):
        return req._debug()

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
