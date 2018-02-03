# RESOURCES #

Xio is builded on concept of resources

- resources:
    
    The main concept is that everything is resource, a resource is a feature which match an uri and we can interact wich 

```

Here is an minimalist example of what app.py look like

```
#-*- coding: utf-8 -*--

import xio 

resource = xio.resource()


if __name__=='__main__':

    resource.expose("http://0.0.0.0:8080")
```


