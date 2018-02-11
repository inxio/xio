
### About xio

Xio is a Python micro framework for quickly write simple microservices REST based Web applications and APIs.

Xio is builded on concept of resources, app , node and network

- resources:
    
    The main concept is that everything is resource, a resource is a feature which match an uri and we can interact wich 

- app:
    
    An app is a root resource used as container for all resources it contain

- node 

    A node is a app gateway, an app (and so a resource) which provide unique checkpoint for resources delivery
    Nodes could be linked beetween for create network 
    
- network 

    A network is a container of nodes and define rules for decentralized backbone of resources 
    

### Requirements

You need Python >= 2.7


### Installation

```
pip install xio
```

### Usage

Basic app creation

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

start server

```
./app.py run 
```


