#!/usr/bin/env python
#-*- coding: utf-8 -*--

import xio

app = xio.app(__name__)

app.put('www', lambda req: 'ext ok www' if req.GET else None)
app.put('www/test', lambda req: 'ext ok test')

