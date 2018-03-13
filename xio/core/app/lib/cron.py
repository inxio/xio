#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class SchedulerService:

    def __init__(self,app,**kwargs):
        import sched
        import time
    
        self._jobs = []
        self.sched = sched.scheduler(time.time, time.sleep)

        
    def schedule(self,when,what,*args,**kwargs):
        
        self._jobs.append((when,what,args))
        self.repeat(when,what,args)

    def repeat(self,interval, func, args):

        interval = int(interval)
        if interval:

            from threading import Event, Thread
            stopped = Event()
            def loop():
                while not stopped.wait(interval):
                    try:
                        func(*args)
                    except Exception as err:
                        print('SchedulerService ERROR', err)

            t = Thread(target=loop)
            t.daemon = True
            t.start()    
            return stopped.set
