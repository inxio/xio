#!/usr/bin/env python
#-*- coding: utf-8 -*--

import unittest

import xio
import sys
from pprint import pprint

import time


class TestCases(unittest.TestCase):


    def test_base(self):

        network = xio.network()
        assert network.id
        assert network.peers


if __name__ == '__main__':

    unittest.main()



