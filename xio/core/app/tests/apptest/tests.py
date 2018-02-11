#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest



class Tests(unittest.TestCase):

    def test1(self):
        from .app import app
        assert app.request('GET','test1').content=='ok test1'

    def test2(self):
        assert True



if __name__=='__main__':

    unittest.main()



    



