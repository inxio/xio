#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import xio 

import unittest

testdata = [
    {
        'field1': 'r1v1',
        'field2': {
            'field21': 'r1v21',
            'field22': {
                'field221': 'r1v221',
                'field222': 'r1v222',
            },    
        },    
        'field3': 'r1v3',
    },
    {
        'field1': 'r2v1',
        'field2': {
            'field21': 'r2v21',
            'field22': {
                'field221': 'r2v221',
                'field222': 'r2v222',
            },    
        },    
        'field3': 'r2v3',
    }
] 

class Tests(unittest.TestCase):

    def test_container(self):

        data = xio.data(testdata)
        assert data.adapt()
        
        
    def test_fields(self):

        data = xio.data(testdata[0])

        r = data.adapt('field1') 
        assert list(r.keys())==['field1']
        r = data.adapt('field1,field3') 
        assert list(r.keys())==['field1','field3']
        r = data.adapt('field2') 
        assert list(r.keys())==['field2'] and r['field2']['field22']['field221']=='r1v221'
        r = data.adapt('field2.field21')
        assert list(r.keys())==['field2'] and list(r['field2'].keys())==['field21'] and r['field2']['field21']=='r1v21'
        r = data.adapt('field3,field2.field22.field222') 
        assert list(r.keys())==['field3','field2'] and list(r['field2'].keys())==['field22'] and list(r['field2']['field22'].keys())==['field222'] and r['field2']['field22']['field222']=='r1v222'

                



if __name__=='__main__':

    unittest.main()





