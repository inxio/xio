#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""

"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId


class Database:


    def __init__(self,name,params):
        #host='localhost', name=None, port=27017, login=None, password=None
        self.name = name.replace('.','_') 
        self.uri = params.get('uri')

        client = MongoClient(self.uri) if self.uri else MongoClient()

        self.db = client[name] 

    def list(self):
        #print 'mongo list'
        cols = self.db.collection_names()
        #print cols
        result = []
        for name in cols:
            collection = self.db[name]
            container = Container( name, collection )
            result.append(container)
        #print 'mongo list', result
        return result


    def get(self,name):
        # warning: mongo db does not return empty collections !!
        collection = self.db[name]
        return Container( name, collection )


    def put(self,name):

        collection = self.db[name]

        #print 'mongo put container', self.name, name
        # fix curiosité mongi qui ne liste pas une ressource sans data
        
        newc = Container( name, collection )
        #newc.put('test',{'result':'testok'})
        return newc


    def delete(self,name):
        #print 'mongo delete container', self.name
        self.db.drop_collection(name)


       


        


class Container:

    def __init__(self,name, collection):
        self.collection = collection
        self.name = name

    def exist(self,id):
        query = {'_id': id}
        row = self.collection.find_one(query)
        return bool(row)

    def get(self,id):
        query = {'_id': id}
        row = self.collection.find_one(query)
        return row


    def select(self,filter=None,fields=None,limit=None,start=0,sort=None,**kwargs):
   
        query = filter2query(filter)
        
        cursor = self.collection.find(query)

        if limit:
            cursor.skip(start)
            cursor.limit(limit)
        if sort:
            mongosort = []
            for s in sort:
                s = s.strip()
                orient = ASCENDING
                if (s.split(' ').pop()=='desc'):
                    orient = DESCENDING
                    s = s.split(' ').pop(0)
                mongosort.append( (s, orient) )

            cursor.sort(mongosort)

        from bson.json_util import dumps


        #
        # tofix : use iterator
        result = []
        for row in cursor:
            result.append(row)
        return result
            



    def post(self,data):
        return self.collection.insert(data)


    def put(self,index,data):
        #attention pb si clé d'un dico ou sous dico contient un point !!!
        #symptome = 'not okForStorage'
        #if '_id' in data:
        #    del data['_id']

        #return self.collection.update(key, {"$set":data}, upsert = True);
        #return self.collection.find_one(key) # permet de recupere le _id (return self.collection.update le renvoi pas forcement)

        query = {'_id': index }
        data = data or {}
        self.delete(index)
        return self.collection.update(query, {"$set":data}, upsert=True); # pb car put faisait une mise a jour



    def update(self,index,data,*args,**kwargs):
        query = {'_id': index }
        if '_id' in data:
            assert data.pop('_id')==index
        return self.collection.update(query, {"$set":data}, upsert=False);


    def truncate(self):
        
        return self.collection.remove({}) 

    def delete(self,index=None,filter=None):
        #print 'mongo db delete', filter
        
        if index:
            query = {'_id': index }
        elif filter:
            query = filter2query(filter)
        else:
            query = {} # tres dangereux
        if query: #tres dangereux donc filtre explicite requis ?
            return self.collection.remove(query) 

    def count(self,filter=None):
        #print 'mongo db count', filter
        query = filter2query(filter)
        cursor = self.collection.find(query)
        return cursor.count() #filter=query ne marche pas ??





        
def filter2query(filter):
    """
    http://docs.mongodb.org/manual/reference/operator/query/
    """
    #print 'filter2query::filter', filter
    query = {}
    filter = filter or {}
    for k,v in filter.items():
        if isinstance(v,tuple):
            operator,v = v
            mop = '$%s' % operator
            value = {mop: v}
        elif isinstance(v,list):
            value = {"$in": v}
        else:
            value = v
        query[k] = value    
            
    """
    if keyword:
        #filter = {'description':{"$regex": keyword}}
        mongokeywordfilter = {"$or": [
            {"description": {"$regex": keyword,'$options':'i'}}, 
            {"title": {"$regex": keyword,'$options':'i'}}
        ]}
        query = {
            "$and": [ query, mongokeywordfilter ]
        }
    """

    #print 'filter2query::query', query
    return query

        




