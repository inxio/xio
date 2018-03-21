#!/usr/bin/env python
#-*- coding: utf-8 -*--


from pprint import pprint
import hashlib

import uuid

def _uid(*args):
    result =  hashlib.md5(':'.join(args)).hexdigest()
    return result

class TasksService:

    def __init__(self,app=None,db=None,heartbeat=10):
        #self.db = app.get('services/database').get('xio_tasks')
        self.app = app
        self._db = self.app.get(db)

        self.db = self._db.get('tasks')
        self.userid = 'DEFAULT'
        self._tasks = {}

        self.app.schedule(int(heartbeat), self.run)

    def run(self):
        data = self.pull()
        if data:
            task = Task(data=data,broker=self)
            task.run()
        
    
    def getTask(self,uid):
        data = self.get(uid) 
        return Task(data=data,broker=self) if not isinstance(data,Task) else data

    def get(self,id):
        return self._tasks[id] if id in self._tasks else self.db.get(id).content


    def put(self,id,handler):
        self._tasks[id] = Task( broker=self, data={'_id': id,'handler': handler})
        return self._tasks[id] 


    def update(self,uid,data):
        self.db.update(uid,data)


    def select(self,filter=None,limit=200):
        filter = filter or {}
        rows = self.db.select( filter=filter,limit=limit)
        return [ row for row in rows ] # ERR_INCOMPLETE_CHUNKED_ENCODING si renvoi direct


    def pull(self):
        # get task
        rows = self.select(filter={'status':[None,0,1,2],'_lock':None}, limit=1) 
        # locktask
        if rows:
            import time
            data = rows[0]
            uid = data['_id']
            data['_lock'] = int(time.time()) 
            self.update(uid,data)
            return data
        return None


    def push(self,data):
        data['status'] = Task.TODO
        uid = str(uuid.uuid4())
        return self.db.put(uid,data)





        


class Task:


    TODO = 0
    PENDING = 1
    RUNNING = 2
    SUCCESS = 9
    ERROR = 8
    DONE = 0

    # flow
    OPEN = 10 # open implique close ? ou open = on peut ajouter des jobs avant de lancer (serait plutot un status init ou setup) ?
    CLOSE = 11

    def __init__(self,data=None,broker=None):
        data = data or {}
        self._data = data
        self.broker = broker
        self.db = broker.db
        self.id = data.get('_id')
        self.pid = data.get('pid')
        self.type = data.get('type')
        self.input = data.get('input')
        self.status = data.get('status')
        self.output = data.get('output')
        self.step = data.get('step',1)
        self.retry = data.get('retry',0)
        self.children = data.get('children') # mapped case
        self.handler = data.get('handler')
        self.error = data.get('error')
        
        if self.type:
            parent = self.broker.getTask(self.type)
            self.flow = parent.flow
        elif self.pid:
            parent = self.broker.getTask(self.pid)
            self.flow = parent.flow
        else:
            self.flow = Flow()
            # gestion des handlers de base  
            if callable(self.handler): 
                import yaml
                config = yaml.load(self.handler.__doc__)

                configflow = config.get('flow')
                if configflow:
                    # gestion flow: STEP1,STEP2,STEP3
                    if isinstance(configflow,basestring):
                        configflow = []
                        for name in config.get('flow').split(','):
                            if name=='MAP':
                                step = {'handler': 'MAP'}
                            elif name=='REDUCE':
                                step = {'handler': 'REDUCE'}
                            else:
                                step = {
                                    'method': name.strip(),
                                    'handler': self.handler
                                }
                            configflow.append(step)

                    for row in configflow:
                        self.flow.append(row)      
            else:
                self.flow.append(self.handler)

        self.steps = len(self.flow )

        self.DONE = self.status in (self.SUCCESS,self.ERROR)
        self._jobs = [] # test sans db

    def __call__(self,req):
        if not req.path:
            if req.GET:
                result = self._data

                # task type vs pid
                if self.id in self.broker._tasks:    
                    # list tasks of this type
                    result['tasks'] = self.broker.select(filter={'type': self.id})
                else:
                    # list child jobs (map/reduce)
                    result['jobs'] = self.broker.select(filter={'pid': self.id})
                result['flow'] = self.flow.serialize()
                return result
            if req.RESET:
                self.broker.db.delete('',data={'filter':{'pid': self.id}})
                self.status = 0
                self.step = 1
                self.retry = 0
                self.save()
                return 'RESET OK'
            if req.RETRY:
                self.status = 0
                self.save()
            if req.PUSH:
                return self.push(req.data)
            if req.RUN:
                return self.run()
        else:

            uid = req.path.split('/').pop(0)
            return self.broker.getTask(uid)

            
    def push(self,input):
        data = {'input': input,'type':self.id}
        return self.broker.push(data)


    def getStepConfig(self):
        return self.flow.get( self.step-1 ) 


    def __repr__(self):
        return 'TASK#%s status=%s step=%s/%s retry=%s input=%s' % (self.id,self.status,self.step,self.steps,self.retry,str(self.input)[0:50]+'...')

    def map(self):
        data = self.input
        
        for row in data:
            self.broker.push({
                'pid': self.id,
                'step': self.step+1,
                'status': 0,
                'input': row,
            })
        self.children = len(data)
        self.status = Task.PENDING
        # set step to next REDUCE JOB
        i = self.step
        for i in range(i,len(self.flow)):
            stepconfig = self.flow.get( i ) 
            if stepconfig.get('handler')=='REDUCE':
                self.step = i+1
                break
        self.save()
        return {}
        
        

    def reduce(self):

        # cas d'un child
        if self.pid:
            self.status = Task.SUCCESS
            self.output = self.input
            self.save()
            return 'DONE'

        # check if all done
        rows = self.broker.select( filter={'pid': self.id} )
                
        alldone = []
        for row in rows:
            status = row.get('status')
            alldone.append( status!=Task.TODO )
         
        if all( alldone ):
            reduced = []
            for row in self._jobs:
                reduced.append(row['output'])
            self.nextStep(reduced)

        self.save() # unlock
        
    def nextStep(self,result):
        if self.step==self.steps:
            self.status = Task.SUCCESS
            self.output = result
        else:
            self.status = Task.TODO
            self.input = result
            self.step = self.step+1
        self.save()


    def save(self):
        self.DONE = self.status in (self.SUCCESS,self.ERROR)

        self.broker.update(self.id,
        {
            '_lock': None,
            'type': self.type,
            'pid': self.pid,
            'step': self.step,
            'status': self.status,
            'retry': self.retry,
            'input': self.input,    
            'output': self.output,
            'children': self.children,
            'error': self.error
        })

    """
    def getHandler(self):
        import xio
        config = self.getStepConfig()

        handler = config.get('handler') if isinstance(config,dict) else config
       
        print 'HANDLER=', handler
    
        if handler=='this':
             handler = self.TaskFactory.handler
             return xio.client( handler )
        elif handler==map:
             handler = self.handleMap
             return handler            
        elif handler==reduce:
             handler = self.handleReduce
             return handler     
        elif callable(handler):
            return xio.client( handler )

        elif isinstance(handler,basestring) and  '/' in handler:
            handler = self.TaskFactory.tasks.app.get(handler).content # pb si on renvoi la resource direct car h(req) return le result et pas l'objet response 
            return xio.client( handler )
    """

    
    def run(self,input=None):
        """
        si 200: DONE
        si 201: batch crée -> RUNNING
        si 202: continue    
        si 500: Failed
        """
        self.steps = len(self.flow )
        self.retry += 1

        stepconfig = self.getStepConfig()
        handler = stepconfig.get('handler')
        method = stepconfig.get('method','POST')
        params = stepconfig.get('params',{})

        # fix handler
        import xio        
        if handler == 'MAP':
            return self.map()
        elif handler=='REDUCE':
            return self.reduce()


        handler = xio.client( handler )
        

        """
        handler = self.getHandler()
        if handler==self.handleMap:
            return self.handleMap()
        elif handler==self.handleReduce:
            return self.handleReduce()
        """

        context = {}

        #print self,'>> RUNNING',handler, self.input

        if self.retry>10:
            self.status = Task.ERROR
            self.save()
            return

        if self.status not in ( Task.TODO, Task.RUNNING ):
            self.save() # pour le retry
            return

        payload = self.input 

        #print self,'>>> CALL HANDLER REQUEST', method, handler, payload
        res = handler.request(method,'',data=payload)
        #print self,'>>> CALL HANDLER RESPONSE', res

        # cas d'un batch

        # cas d'un traitement direct
        if res.status==200:
            self.nextStep(res.content)
        elif res.status==201:
            self.status = Task.RUNNING
            self.input = res.content
            self.save()
        elif res.status==202:
            self.input = res.content
            self.save()
        elif res.status==500:
            self.status = Task.ERROR
            self.save()
        return self



class Flow:
    
    def __init__(self,parent=None):
        self._flow = []
        self._parent = parent

    def serialize(self):
        result = []
        for row in self._flow:
            result.append(row)
        return result
        

    def debug(self):

        for i,step in enumerate(self._flow):

            if isinstance(step,Flow):
                step.debug()
            else:
                prefix = '\t' if self._parent else''


    def __len__(self):
        return len(self._flow)

    def get(self,step):
        return self._flow[step]

    def append(self,handler):
        if isinstance(handler,list):
            subflow = self.map()
            for row in handler:
                subflow.append(row)
            return subflow.reduce()      
        else:
            self._flow.append(handler)   


    def do(self,handler):
        self._flow.append(handler)
        return self

    def map(self):
        flow = Flow(self) 
        self._flow.append( map )
        self._flow.append( flow )
        return flow

    def reduce(self):
        parent = self._parent
        parent.do( reduce )
        return self._parent





if __name__=='__main__':
    
    import time
    from pprint import pprint    

    def h1(req):
        data = req.data
        data.update({'h1': 'ok1'})
        return data   
 
    def h2(req):
        data = req.data
        data.update({'h2': 'ok2'})
        return data 
    
    task = Task()
    task.flow.append( lambda req: [ {'id':i} for i in range(1,10) ] )
    task.flow.append( [h1,h2] ) 
    task.flow.append( lambda req: {'total': len(req.data),'result': req.data } )

    task.run( {} )

    while True:
        print ('waiting tasks ...')
        time.sleep(1)



    """

    flow = Flow()
    flow.append( lambda req: [ {'id':i} for i in range(1,10) ] )
    flow.append( [h1,h2] ) 
    flow.append( lambda req: {'total': len(req.data),'result': req.data } )
    flow.run()

    task = Task( handler )
    task.run( )

    """




