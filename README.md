# README #

### About xio

Xio is a Python micro framework for quickly write simple microservices REST based Web applications and APIs.

This package provide out of the box theses components :

- an app server component for HTTP/HTTPS delivery

- 3 app clients for interact whith server in PYTHON, PHP and JAVASCRIPT

Xio is builded on concept of resources, app and node

- resources:
    
    The main concept is that everything is resource, a resource is a feature which match an uri and we can interact wich 

- app:
    
    An app is a root resource used as container for all resources it contain

- node 

    A node is a app gateway, an app (and so a resource) which provide unique checkpoint for resources delivery
    Nodes could be linked beetween for create network and so provide decentralized backbone of resources 
    
    

### Requirements

You need Python >= 2.7

The server component use [Gevent ](https://pypi.python.org/pypi/gevent) 

The (python) client component has no dependency except [ws4py](https://pypi.python.org/pypi/ws4py/0.3.5) if you need Websockets features


### Installation

Clone xio in a directory which is in your pythonpath

```
cd xio
sudo pip install -r requirements.txt
```

### Create first app

Create your application directory and edit an app.py file

```
mkdir myfirstapp
cd myfirstapp
vi app.py
```

Here is an minimalist example of what app.py look like

```
#-*- coding: utf-8 -*--

import xio 

app = xio.app(__name__)

@app.bind('www')
def _(req):
    return 'Hello World'

if __name__=='__main__':

    app.main()
```


### the request object

In the previous example we bind the root public resource ('www') of our app to an anonymous function which in charge to rendering the client request

These function are called handler, all handler took one single argument : req 

req is the Request instance whiche provide these information

    - req.method : the HTTP standard method (GET,POST,PUT,etc...)
    - req.query : the query in the case of a GET request (in a dict)
    - req.data : the data in the case of a POST,PUT request (in a dict)
    - req.headers : the request headers
    - req.path : the postpath of the request
    - req.response : the Response object
    - req.profile : the data profile (extra information from the header)

In addition an dynamique attribute is automaticaly added depending the method of the request, 
```
if req.method=='GET':
    do some stuff...
``` 
could be wrote
```
if req.GET:
    do some stuff...
``` 
     

req.response is the Response instance for this request

    - req.response.status : for setting the HTTP code
    - req.response.content : the content of the response (automaticaly took from the handler result)
    - req.response.content_type : for setting the content_type of the request
    - req.response.headers : the headers of the response (dict)


Here is an example of request from client and serveur

```
import xio

app = xio.app()

@app.bind('www')
def _(req):
    if req.GET:
        return 'it is a GET request'
    else:
        return 'it is a %s request' % req.method


```

Here is an minimalist example of what app.py look like

```
#-*- coding: utf-8 -*--

import xio 

app = xio.app(__name__)

@app.bind('www')
def _(req):
    return 'Hello World'

if __name__=='__main__':

    app.main()
```


