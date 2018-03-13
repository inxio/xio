#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
from pprint import pprint
import traceback
import json
import base64
import uuid

from threading import Thread, current_thread

import gevent

from gevent.event import Event
from gevent.queue import Queue, Empty
from gevent.select import select

class Wshandler:

    def __init__(self, fd, session , send_event, send_queue, recv_event, recv_queue):

        self.fd = fd    
        self.session   = session
        self.session._send = self.send

        self.send_event = send_event
        self.send_queue = send_queue
        self.recv_event = recv_event
        self.recv_queue = recv_queue
        self.timeout    = 10
        self.connected  = True


    def send(self, msg):
        self.send_queue.put(msg)
        self.send_event.set()


    def close(self):
        print('CLOSE CONNECTION')
        self.connected = False

    def __call__(self):

        while self.connected:
            msg = self.recv_queue.get()
            self.session.onreceive(msg)


class WebsocketService:
    
    def __init__(self,app=None,path='',port=0,context=None):
        self.app = app
        self.path = path
        self.port = port
        self.context = context
        self._wssockets = {}
       

    def start(self):
        # mod TEST ONLY
        from gevent import monkey; monkey.patch_all()
        from ws4py.server.geventserver import WSGIServer
        from ws4py.server.wsgiutils import WebSocketWSGIApplication
        from ws4py.websocket import WebSocket

        class _WebSocketSession(WebSocket):

            def __init__(self,wsservice,*args,**kwargs):
                WebSocket.__init__(self,*args,**kwargs)
                uid = base64.urlsafe_b64encode(uuid.uuid4().bytes).strip("=")
                self.wsservice = wsservice
                self.ws = WebsocketSession(uid,wsservice.app,{}) 
                self.ws._send = self.send_message

            def opened(self):
                self.wsservice.onconnected(self.ws)

            def closed(self,code,reason):
                self.wsservice.ondisconnected(self.ws)

            def send_message(self,msg):
                self.send(msg)

            def received_message(self,msg):
                self.ws.onreceive(msg)

        def _createsession(*args,**kwargs):
            wsSession = _WebSocketSession(self,*args,**kwargs)
            return wsSession

        server = WSGIServer(('localhost', self.port), WebSocketWSGIApplication(handler_cls=_createsession))
        server.serve_forever()


    def onconnected(self,ws):
        self.app.publish('onWsConnected',ws)
        self.app.put('run/websockets/%s' % ws.uid,ws)
        
    def ondisconnected(self,ws=None):
        self.app.publish('onWsDisconnected',ws)
        self.app.delete('run/websockets/%s' % ws.uid)
        


    def __call__(self,environ,start_response=None):

        import uwsgi

        uwsgi.websocket_handshake(environ['HTTP_SEC_WEBSOCKET_KEY'], environ.get('HTTP_ORIGIN', ''))

        # setup session
        uid = base64.urlsafe_b64encode(uuid.uuid4().bytes).strip("=")
        session = WebsocketSession(uid,self.app,environ) 

        # setup wshandler

        websocket_fd = uwsgi.connection_fd()
        send_event = Event()
        send_queue = Queue(maxsize=100)
        recv_event = Event()
        recv_queue = Queue(maxsize=100)

        ws = Wshandler(websocket_fd,session,send_event,send_queue,recv_event,recv_queue)

        # register fot http call
        self._wssockets[uid] = ws

        # spawn it
        wsd = gevent.spawn( ws )

        ############# EVENT HANDLING

        # gevent.spawn recv listener
        def listener(fd):
            select([ws.fd], [], [], 10)
            recv_event.set()

        listening = gevent.spawn(listener, ws)

        while True:

            gevent.wait([send_event,recv_event], None, 1)

            if not ws.connected:
                recv_queue.put(None)
                listening.kill()
                wsd.join(ws.timeout)
                return ''

            # send :   session -> (send_queue) -> uwsgi -> client
            if send_event.is_set():
                try:
                    msg = send_queue.get_nowait()
                    print('uwsgi.send >>>', msg)
                    uwsgi.websocket_send(msg)
                except Empty:
                    send_event.clear()
                except IOError:
                    print('IOError')
                    ws.close() 
                except Exception as err:
                    print('ERROR', err)

            # receive :   client -> uwsgi -> (receiv_queue) -> session
            if recv_event.is_set():
                recv_event.clear()
                try:
                    msg = uwsgi.websocket_recv_nb()
                    if msg:
                        print('uwsgi.receive <<<', msg)
                        recv_queue.put(msg)
                        listening = gevent.spawn(listener, ws)
                except IOError:
                    print('IOError')
                    ws.close()

            if wsd.ready(): 
                listening.kill()
                return ''




class WebsocketSession:
    
    def __init__(self,uid,app,context):
        self.uid = uid
        self.app = app
        self.handler = app
        self.context = context
        self.context['websocket'] = self
        self._awaiting_requests = {}
        self.remoteapp = None
        self._topics = {}
        self._send = None
        self._listen = None
        self.path = ''

        
    def subscribe(self,topic,callback): # test
        self._topics.setdefault(topic,[])
        if not self._topics[topic]:
            self.send({
                'type': 'subscribe',
                'topic': topic,
            })
        self._topics[topic].append(callback)


    def __repr__(self):
        return 'WebSocketSession %s' % self.uid        

    def head(self,*args,**kwargs):  
        return self.request('HEAD',*args,**kwargs)

    def get(self,*args,**kwargs):  
        return self.request('GET',*args,**kwargs)

    def post(self,*args,**kwargs): 
        return self.request('POST',*args,**kwargs)

    def put(self,*args,**kwargs):  
        return self.request('PUT',*args,**kwargs)

    def delete(self,*args,**kwargs):  
        return self.request('DELETE',*args,**kwargs)


    def request(self,method,path,query=None,data=None,headers=None,context=None,**kwargs):  
        print('WebsocketClient request', method)
        import xio
        req = xio.request(method,path,query=query,data=data,headers=headers,context=context)        
        return self(req)



    def __call__(self,req):

        message = {
            'method':   req.method,
            'path':     req.path,
            'data':     req.data,
            'query':    req.query,
            'headers':    req.headers,
        }
        resp = self.send(message)
        req.response.code = resp.get('status')
        req.response.headers = resp.get('headers') or {}
        req.response.content = resp.get('content')
        return req.response



    def send(self,msg):

        if isinstance(msg,dict):
            msgtype = msg.get('type')
            if msgtype=='about':
                self._send( json.dumps(msg) )
            elif 'method' in msg:
                import uuid
                id = str( uuid.uuid4() )
                msg['type'] = 'request'
                msg['id'] = id
                self._awaiting_requests[id] = None
                self._send( json.dumps(msg) )
                
                timeout = 5
                t0 = time.time()
                while self._awaiting_requests.get(id)==None:
                    t1 = time.time()
                    s = int(t1-t0)    
                    print('gevent.waiting ... since', int(t1-t0)) 
                    if s>timeout:
                        return {
                            'status': 408,
                            'content': '',
                            'headers': {}
                        }
                    gevent.sleep(0.1)
                print('RESPONSE FOUND', self._awaiting_requests)
                return self._awaiting_requests.pop(id)
            else:
                self._send( json.dumps(msg) )
        else:
            self._send( msg )   



    def onreceive(self,msg):
        try:
            msg = json.loads(str(msg))
        except:
            msg = {}

        msgtype = msg.get('type')
        id = msg.get('id')
        if msgtype=='publish': 
            topic = msg.get('topic')
            mess = msg.get('msg')
            for callback in self._topics.get(topic,[]):
                callback(mess)
        elif msgtype=='response':
            self._awaiting_requests[id] = msg
        elif msgtype=='request':
            method = msg['method']
            path = msg['path']
            path = self.path+path if self.path else path 
            data = msg.get('data')
            query = msg.get('query')
            headers = {} 
            for k,v in list(msg.get('headers',{}).items()):
                headers[k.lower().replace('-','_')] = v   

            context = self.context

            def _feedback(msg):
                msg = {
                    'type': 'feedback',
                    'id': id,
                    'msg': msg
                }
                self._send( json.dumps(msg,default=str) )

            def _onpubsubreceive(msg):
                msg = {
                    'type': 'channel',
                    'id': path,
                    'msg': msg
                }
                self._send( json.dumps(msg,default=str) )

            if method=='POST' and headers.get('xio_method')=='SUBSCRIBE':
                data = _onpubsubreceive
                
            import xio
            req = xio.request(method,path,query=query,data=data,headers=headers,context=context)
            result = self.handler(req)
            response = req.response
            response.content = result

            import inspect
            if inspect.isgenerator(response.content):

                while True:
                    try:
                        content = next(response.content)
                        msg = {
                            'id': id,
                            'type': 'fragment',
                            'content': content
                        }
                        self._send( json.dumps(msg, skipkeys=True, default=str) )
                    except StopIteration:
                        self._send(json.dumps({
                            'id': id,
                            'type': 'response',
                            'content': ''
                        })) 
                        break
            else:

                msg = {
                    'id': id,
                    'type': 'response',
                    'status': response.status,
                    'headers': response.headers,
                    'content': response.content
                }
                self._send( json.dumps(msg,default=str) )




