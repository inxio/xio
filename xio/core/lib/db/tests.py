#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import xio 

import unittest
from pprint import pprint
import sys

from .db import db as database

db = database()


class Tests(unittest.TestCase):


    def test_base(self):

        # create container
        tb1 = db.put('tb1')
        assert tb1
        assert tb1.count()==0

        # container crud
        assert tb1.put('id1',{'name':'item1'})
        assert tb1.count()==1
        assert tb1.update('id1',{'name':'item1 updated'})
        assert tb1.get('id1').get('name')=='item1 updated'
        assert tb1.delete('id1')
        assert not tb1.get('id1')


    def _test1_create_container(self):
        db.delete('tbtest0')
        assert db.put('tbtest0').status==201
        db.delete('tbtest0')

    def _test1_delete_container(self):
        db.truncate('tbtest2').status
        db.delete('tbtest2').status

        assert db.put('tbtest2').status==201
        assert db.put('tbtest2/ID01',{'name':'item1'}).status==201
        assert len( db.get('tbtest2').content) == 1
        assert db.count('tbtest2').content == 1

        # prevent non empty container delete
        assert db.delete('tbtest2').status == 409
        assert db.truncate('tbtest2').status==200
        assert db.delete('tbtest2').status == 200


    def _test1_list_container(self):
        containers = db.get().content
        assert len(containers)==1

    def _test2_create_item(self):

        tbtest1 = db.get('tbtest1')
        assert tbtest1.put('ID01', {'name': 'test1'}).status==201
        assert tbtest1.put('ID02', {'name': 'test2'}).status==201


    def _test3_select_items(self):

        tbtest1 = db.get('tbtest1')
        items = tbtest1.select()
        assert len(items.content)==3



    def _test4_get_item(self):

        tbtest1 = db.get('tbtest1')
        assert tbtest1.get('ID01').status==200
        assert tbtest1.get('ID01').content['name']=='test1'
        assert tbtest1.get('ID02').status==200
        assert tbtest1.get('ID02').content['name']=='test2'


    def test_filter(self):

        tb = db.container('test')
        data = {
            'field1': 'value1',
            'field2': {
                'field21': 'value21',
                'field22': {
                    'field221': 'value221',
                    'field222': 'value222',
                },    
            },    
            'field3': 'value3',
        }

        
    def test_fields(self):

        tb = db.container('test')

        # nested data and field select
        data = {
            'field1': 'value1',
            'field2': {
                'field21': 'value21',
                'field22': {
                    'field221': 'value221',
                    'field222': 'value222',
                },    
            },    
            'field3': 'value3',
        }
                
        tb.put('item1',data)

        # full data
        item = tb.get('item1')
        assert item['field1']=='value1'
        assert item['field2']['field21']=='value21'
        assert item['field2']['field22']['field222']=='value222'

        # get item 
        r = tb.get('item1',fields=['field3','field2.field22.field222'])
        assert list(r.keys())==['field3','field2'] and list(r['field2'].keys())==['field22'] and list(r['field2']['field22'].keys())==['field222'] and r['field2']['field22']['field222']=='value222'

        # select
        r = list(tb.select(fields=['field3']))

        assert list(r[0].keys())==['field3'] 



if __name__=='__main__':

    unittest.main()





