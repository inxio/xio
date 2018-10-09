(function(){

    var standard_method = ['GET','PUT','POST','PATCH','DELETE','HEAD']





    XioResponse = function(status,content,headers) {
        this.status = status || 0
        this.content = content
        this.headers = headers || {}
        return this
    }

    XioRequest = function(method,path,data,headers,context) {
        this.method = method
        this.path = path || ''
        this.data = data || {}
        this.query = data // to fix
        this.headers = headers || {}
        this.context = context || {}
        this[method.toUpperCase()] = true;
        this.client = xio.context.user
        this.response = new XioResponse()
        return this
    }



    XioLogger = function() {
        this.level = 'INFO'
        this.data = []
        this._log = function(level,msg) {
            if (!this.level)
                return
            var args = $.makeArray(arguments).sort().slice(3)
            if (args)
                console.log('['+level+'] '+msg,args)
            else
                console.log('['+level+'] '+msg)
        }
        this.info = function(msg) {
            this._log('INFO',msg, arguments)
        }
        this.debug = function(msg) {
            if (this.level=='DEBUG')
                this._log('DEBUG',msg, arguments)
        }
        this.warning = function(msg) {
            this._log('WARNING',msg, arguments)
        }
        this.error = function(msg) {
            this._log('ERROR',msg, arguments)
        }
        return this
    }


    XioCache = function() {
        this.data = {}
        this.get = function(id) {
            var row =  this.data[id]
            if (row) {
                var now = Date.now()
                if (now>row.ttl) {
                    delete this.data[id]
                } else {
                    console.log('.................... FOUND CACHE ',id, row)
                    return row.content
                }
            }
        }
        this.put = function(id,content,ttl) {
            this.data[id] = {
                'content': content,
                'created': Date.now(),
                'ttl': Date.now()+(ttl*1000)
            }
        }
        return this
    }

    XioScheduler = function() {
        this.data = {}
        this.put = function(id,t,handler) {
            if (this.data[id]) {
                clearInterval(this.data[id]);
            }
            // put 0 for remove schedule
            if (t) {
                this.data[id] = setInterval(handler, t*1000);
            }
        }
        this.get = function(id) {
            return this.data[id]
        }
        return this
    }




    XioHandlers = function() { 
        this._handlers = {}
        return this
    }
    XioHandlers.prototype.bind = function (scheme,handler) {
        this._handlers[scheme] = handler
    }    
    XioHandlers.prototype.get = function (uri) {
        // quick check for direct binding
        var handler = null
        var protocol = ''
        var hostname = ''
        var path = ''

        if (this._handlers[uri]) {
            var handler = this._handlers[uri]
            var protocol = uri
            var hostname = ''
            var path = ''
        } else {
            try {
                // parse uri
                var info = new URL(uri)
                var protocol = info.protocol.slice(0,-1)
                var handler = this._handlers[protocol]
                var path = info.pathname
                var hostname = info.hostname
            } catch (e) {
                xio.log.error('HANDLER NOT FOUND ',uri)
            }
        }

        return {
            'handler': handler,
            'protocol': protocol,
            'path': path,
            'hostname': hostname,
            'uri': uri
        }
    } 





    XioRoutes = function() { 
        this._routes = {}
        return this
    }
    XioRoutes.prototype.bind = function (path,handler) {
        this._routes[path] = {
            'handler': handler
        }
    }    
    XioRoutes.prototype.hook = function (path,hook) {
        this._routes[path].hook = hook
    }    
    XioRoutes.prototype.getHandler = function (path) {

        var route = this._routes[path]
        if (route) {
            return {
                'handler': route.handler,
                'hook': route.hook,
                'context': {},
                'postpath': ''
            }
        }
        for (var route in this._routes) {
            
            var myRegexp = /(?:^|\s)format_(.*?)(?:\s|$)/g;

            var p = route.split('/')
            var pattern = []
            var urlparams = []
            for (var i in p) {
                var part = p[i]     
                if (part.charAt(0)==':') {
                    urlparams.push(part)
                    part = '([^\/]*?)'
                } else if (part=='*') {
                    urlparams.push(part)
                    part = '(.*?)'
                }
                pattern.push(part)
            }
            pattern = pattern.join('\/')
            pattern = '^'+pattern+'$'
            
            var rpattern = new RegExp(pattern,'gi')    
            var rmatch = rpattern.exec(path);
            
            if (rmatch) {
                var info = this._routes[route]
                var params = {}
                
                var rpattern = new RegExp(pattern,'gi') 
                var m = rpattern.exec(path)
                
                for (var i = 0; i < urlparams.length; i++) {
                    params[urlparams[i]] = m[i+1]
                }
                params[urlparams[0]] = m[1]
                params[urlparams[1]] = m[2]
                params[urlparams[2]] = m[3]
                var postpath = ''

                return {
                    'handler': info.handler,
                    'hook': info.hook,
                    'context': params,
                    'postpath': params['*'] || postpath
                }
            }           
        }
        
    }

    function getHandler(uri) {
        var info = xio.handlers.get(uri)
        if (info.handler) {
            handler = new info.handler(uri)
            handler_path = ''
        } else {
            handler = null
            handler_path = ''
        }

        /*
        handler = null
        handler_path = null
        if (endpoint) {
            endpoint = String(endpoint)
            nfo = endpoint.split('/')
            endpoint = nfo[0]+'//'+nfo[2]
            endpoint = endpoint
            handler_path =  '/'+nfo.slice(3).join('/')
            
            if (endpoint.substring(0, 7) == "http://" || endpoint.substring(0, 8) == "https://" ) {
                var handler = new httpHandler(endpoint)
            } else if (endpoint.substring(0, 5) == "ws://" || endpoint.substring(0, 6) == "wss://" ) {
                var handler = new websocketHandler(endpoint)
            } else {
                var handler = null
            }
        }
        return [handler,handler_path]
        */
        return [handler,handler_path]
    }
    
    XioResource = function(kwargs) {

        if (kwargs && typeof(kwargs) != "object") {

            var info = getHandler(kwargs)

            // gestion defered gethandler
            handler = info[0]
            handler_path = info[1]

            kwargs = {
                'handler': handler,
                'handler_path': handler_path        
            };
        } else if (kwargs && kwargs.render) {
            kwargs = {
                'handler': kwargs,    
            };
        } else {
            kwargs = kwargs || {}
        }
    

        this._children = new XioRoutes()
        this._handler = kwargs.handler
        this._handler_path = kwargs.handler_path || ''
        this.path = kwargs.path || ''
        this.status = kwargs.status || 0
        this.headers = kwargs.header || {}
        this.content = kwargs.content 
        this.context = kwargs.context || {}
        this._cache = new XioCache()
        return this
    }
    XioResource.prototype.bind = function (path,handler) {
        if (path=='*')
            this._fallback = handler
        else
            this._children.bind(path,handler)
    }
    XioResource.prototype.about = function(path) { return this.request('ABOUT',path) }
    XioResource.prototype.get = function(path,query) { return this.request('GET',path,query) }
    XioResource.prototype.put = function(path,data) { return this.request('PUT',path,data) }
    XioResource.prototype.patch = function(path,data) { return this.request('PATCH',path,data) }
    XioResource.prototype.post = function(path,data) { return this.request('POST',path,data) }
    XioResource.prototype.delete = function(path) { return this.request('DELETE',path) }
    XioResource.prototype.request = function (method,path,data,headers,context) {
        var self = this
        path = path || ''
        // check if method is request instance
        if (method.method) {
            var req = method
            path = req.path
            data = req.data
            method = req.method
            headers = req.headers
            context = req.context
        }

        var cacheuid = false
        /*
        tofix: pb de gestion resp/content

        if (method=='GET' || method=='ABOUT') {
            if (!data) { // to fix ... need to handle query
                var cacheuid = xio.tools.md5(method,path) 
                var cached = this._cache.get(cacheuid)
                if (cached) {
                    console.log('.................... FROM CACHE ?',cacheuid, cached)
                    return cached
                }
            }
        }
        */
        console.debug('.................... REQUEST',method,path,'by',this)
        //xio.log.debug('.................... REQUEST',method,path,'by',this)

        var result = null
        if (this._handler && this._handler.request) {
            var result = this._handler.request(method,path,data)
        } else if (this._handler && this._handler.render) {
            var req = xio.request(method,path,data,headers,context)
            var result = this._handler.render(req)
        } else {
            p = path
            if (p && p[0]=='/')
                p = p.slice(1)

            var info = this._children.getHandler(p)

            if (!info && this._fallback) {
                console.debug('.................... REQUEST use fallback')
                info = {
                    'handler': this._fallback,
                    'postpath': path,
                    'context': {},
                }
            }

            if (info) {
                var handler = info.handler
                var postpath = info.postpath
                var context = info.context
                var req = xio.request(method,postpath,data,{},context)
                var result = handler.call(this, req)
            } 
        }
        
        var d = $.when(result).then(function(resp) {

            console.log('---------RESP1---------',resp)

            if (!(resp instanceof XioResource)) {

                if (!(resp instanceof XioResponse)) {
                    resp = new XioResponse(resp.status, resp.content, resp.headers)
                }
                var res = new XioResource(resp)
            } else {
                var res = resp
            }
            //console.log('---------RESP1---------',res)
            
            //xio.log.debug('.................... RESPONSE',res.status,res.content,res)

            return res
        })
        if (cacheuid)
            self._cache.put(cacheuid,d,3600)


        return d

    }

    XioApp = function(endpoint,context) {
        XioResource.call(this,endpoint,context);
        return this
    }
    XioApp.prototype = Object.create(XioResource.prototype, {
        constructor: { value: XioApp }
    });


    /*

    XioApp = function(endpoint,params) {
        params = params || {}
        xio.log.debug('create xio app to '+endpoint+'...')
        nfo = endpoint.split('/')
        endpoint = nfo[0]+'//'+nfo[2]
        this._endpoint = endpoint
        this._basepath =  '/'+nfo.slice(3).join('/')
        this._profile = params
        this._root = new XioResource(this,'')

        this._token = params['token']
        if (endpoint.substring(0, 7) == "http://" || endpoint.substring(0, 8) == "https://" ) {
            this._handler = new httpHandler(endpoint)
        } else if (endpoint.substring(0, 5) == "ws://" || endpoint.substring(0, 6) == "wss://" ) {
            this._handler = new websocketHandler(endpoint)
        } else {
            xio.log.debug('unknow handler', endpoint)
        }

        this.log('connected', this._handler)
        this.log('endpoint', this._endpoint )
        this.log('basepath', this._basepath )

        return this
    }
    XioApp.prototype = {

        get: function(path,query) { return this._root.get(path,query) },
        put: function(path,data) { return this._root.put(path,data) },
        post: function(path,data) { return this._root.post(path,data) },
        delete: function(path) { return this._root.delete(path) },
        patch: function(path,data) { return this._root.patch(path,data) },
        about: function(path,query) { return this._root.about(path,query) },
        api: function(path,query) { return this._root.api(path,query) },
        connect: function(path,query) { return this._root.connect(path,query) },

        subscribe: function(path,callback) { return this._root.subscribe(path,{'channel':path,'callback':callback}) },

        log: function(msg) {  },

        request: function(method,path,query,callback,errback,feedback,profile) { 
            //xio.log.debug('app request',method,path,query)
            //xio.log.debug('app token',this._token)
            if (this._basepath && this._basepath.slice(-1)!='/' && path && path[0]!='/')
                path = this._basepath+'/'+path
            else if (this._basepath && this._basepath.slice(-1)=='/' && path && path[0]=='/')
                path = this._basepath+path.slice(1)
            else
                path = this._basepath+path
            //xio.log.debug('app request',method,path,query)
            var headers = {
            }
            if (this._token) {
                headers['Authorization'] = 'xio/ethereum '+this._token
            }
            if (this._profile) {
                if (typeof this._profile === 'string' || this._profile instanceof String) {
                    headers['XIO-profile'] = this._profile 
                } else {
                    headers['XIO-profile'] = JSON.stringify(this._profile)
                }
            }
            // gestion XIO-method

            if (standard_method.indexOf(method)<0) {
                headers['XIO-method'] = method
                method = 'POST'
            }

            var req = this._handler.request(method,path,query,headers,callback,errback,feedback)
            return req
        }
    }
    */



    XioDb = function(name) {
        this._name = name
        if (name) {
            this._db = JSON.parse( localStorage.getItem('xio.db.'+this._name) || '{}')  
        } else {
            this._db = {}
        }
        return this
    }
    XioDb.prototype.select = function (filter) {
        filter = filter || {}
        var result = []
        for (var index in this._db) {
            var row = this._db[index]
            row = JSON.parse(JSON.stringify(row))
            if (typeof filter === "function") {
                var check = filter(row)
            } else {
                var check = true
                for (var key in filter) {
                    check = check && (row[key]==filter[key])
                }
            }
            if (check) {
                result.push(row)
            }
        }
        return result
    }
    XioDb.prototype.put = function (index,data) {
        this._db[index] = data
        this.commit()
    }
    XioDb.prototype.patch = function (index,data) {
        var row = this._db[index]

        for(var key in data) {
            row[key] = data[key]
        }
        this._db[index] = row
        this.commit()
    }
    XioDb.prototype.delete = function (index) {
        delete this._db[index]
        this.commit()
    }
    XioDb.prototype.get = function (index) {
        var row = this._db[index]
        if (row) {
            // clone row for prevent object post update
            row = JSON.parse(JSON.stringify(row))
        }
        return row
    }
    XioDb.prototype.commit = function (index) {
        if (this._name) {
            localStorage.setItem('xio.db.'+this._name,JSON.stringify(this._db))
        }
    }
    XioDb.prototype.truncate = function () {
        this._db = {}
        this.commit()
    }




    websocketHandler = function(endpoint) {
        this._endpoint = endpoint
		this.url = endpoint;
		this.connected = false;
		this.ws = null;
		this._channels = {};
		this._responses = {}; 	// requetes recus en attente de réponse
		this._requests = {};	// requetes envoyées en attente de réponse
		this._feedbacks = {};	// feedback recu lié a une requete envoyées en attente de réponse
		this.disconnect = function( callback ) { 
			this.log('close socket...')
			this.ws.close();
			this.connected = false;
			if (callback) {
				callback();
			}
		}
		this.connect = function( callback ) {
		    if (!this.connected) {
		        this.log('connecting websocket...')
                var wshandler = "MozWebSocket" in window ? 'MozWebSocket' : ("WebSocket" in window ? 'WebSocket' : null);
                if (wshandler == null) {
                    alert("Your browser doesn't support Websockets.");
                    return;   
                }
		        this.ws = new window[wshandler](this.url); //new WebSocket(this.url);
		        this.ws.parent = this
                var self = this
		        this.ws.onopen = function(e) { 
					this.parent.connected = true;
					xio.log.debug('websocket connected to '+this.parent.url);
					if (callback) {
						callback(this);
					}
				}
		        this.ws.onmessage = function(e) { 
		            this.parent.log('RECEIVE <<< '+e.data); 
		            var data = JSON.parse(e.data);
		            var type = data['type'];
					var action = data['action']
					var msg = data['msg'];
				    var id = data['id']
					if (type=='response') {
						var callback = this.parent._requests[id]
						callback( data )
					} else if (type=='fragment') {
						var feedback = this.parent._feedbacks[id]
						if (feedback) 
                            feedback( msg )
					} else if (type=='feedback') {
						var feedback = this.parent._feedbacks[id]
						if (feedback) 
                            feedback( msg )
					} else if (type=='channel') {
						var callback = this.parent._channels[id]
						if (callback) 
                            callback( msg )
					} 
		      
		        };
		        this.ws.onerror = function(e) { xio.log.debug('ERROR '+e); };
		        this.ws.onclose = function() { 
                    this.parent.connected = false; 
                    xio.log.debug('disconnected');

                };
		    } 
		}


		this.send = function(msg) {
            msg = JSON.stringify( msg);
		    //this.log('SEND >>> '+msg);
		    this.ws.send(msg);
		}

		this.log = function(msg) {
		    xio.log.debug('xiowebsocket '+this.url+' '+msg)
		}
		this.get = 	function(path,params,callback,errback,feedback) 	{ return this.request('GET',path,params,callback,errback,feedback) } 
		this.post = function(path,params,callback,errback,feedback) 	{ return this.request('POST',path,params,callback,errback,feedback) }

		this.request = function(method,path,params,headers,callback,errback,feedback) {



            if (!this.connected) {
                xio.log.debug('must reconnect for request')
                var self = this;
                return this.connect(function(){
                    self.request(method,path,params,headers,callback,errback,feedback)
                })
            }

            if (headers['XIO-method']=='SUBSCRIBE') {
                this._channels[path] = params['callback']
                params = {}
            }

			if (typeof params == "function") {
				feedback = errback
				errback = callback
				callback = params
			}


			var uid = Math.random().toString(36).substring(2, 15)
            
            var data = {}

			var msg = {
				id: uid,
				type: 'request',
				method: method,
				path: path,
				query: params,
                headers: headers,
                data: data
			};
			this._requests[uid] = callback
            this._feedbacks[uid] = feedback


		    this.send( msg );


			xio.log.debug('REQUEST '+method+' '+path+' '+params)
			//xio.log.debug(callback);
			//xio.log.debug(headers);
		    //callback()
		}
		return this
	}


    httpHandler = function(endpoint) {
        this._endpoint = endpoint

        this.request = function (method,path,params,headers) { //,callback,errback,feedback
            // path doit etre absolut
            // resolve query in path
            var info = parseUrl(path)
            path = info.path
            params = params || info.query

            if (path.charAt(0)!='/')
                path = '/'+path

            var path = this._endpoint+path  


            xio.log.debug('params',params)

		    function urlParams(params) {
			    var params = params || null
			    if (params) {
				    params_out = []
				    for (i in params) {
					    value = params[i]
					    if (value || value===0 || value==='') params_out.push(i+'='+encodeURIComponent(value))
				    }
				    params = params_out.join('&')
			    } else {
				    params = ''
			    }
			    return params
		    }

            function parseUrl(url) {
                var info = url.split('?')
                var hash = info[0];
                var query = info[1];
                var params = {}
                if (query) {
                    var vars = query.split('&');
                    for (var i = 0; i < vars.length; i++) {
                        var pair = vars[i].split('=');
                        var key = decodeURIComponent(pair[0]);
                        var val = decodeURIComponent(pair[1]);
                        params[key] = val
                    } 
                }
                return {
                    'path': info[0],
                    'query': params
                }
            }

            function parseHeaders(raw) {
                // src: https://gist.github.com/monsur/706839
                var headers = {};
                var headerPairs = raw.split('\u000d\u000a');
                for (var i = 0; i < headerPairs.length; i++) {
                    var headerPair = headerPairs[i];
                    // Can't use split() here because it does the wrong thing
                    // if the header value has the string ": " in it.
                    var index = headerPair.indexOf('\u003a\u0020');
                    if (index > 0) {
                      var key = headerPair.substring(0, index);
                      var val = headerPair.substring(index + 2);
                      headers[key] = val;
                    }
                }
                return headers;
            }

		    var parseResult = function(xhr) {
                //xio.log.debug('HEADERS ??',xhr.getAllResponseHeaders() )
            
			    var content_type = xhr.getResponseHeader('content-type')
			    if (content_type=='application/json') {
				    content = JSON.parse(xhr.responseText);
			    } else {
				    content = xhr.responseText
			    }
                return {
                    'content': content,
                    'status': xhr.status,
                    'headers': parseHeaders( xhr.getAllResponseHeaders() )
                }
		    }

            params = params || {}
            data = null
            if (typeof params==='object') {
		        if (method=='POST' || method=='PUT' || method=='PATCH') {
			        var data = new FormData();  
			        for (i in params) {
				        data.append(i, encodeURIComponent(params[i]));
			        }
			        var params = ''
		        } else {
			        var params = urlParams(params)
			        var data = null
		        }
            } else if (params) {
                var data = params
                var params = ''
            }


		    var url = path
		    if (params) 
		        url = url+'?'+params

            var d = $.Deferred()
		    var xhr = new XMLHttpRequest();

            xhr.open( method, url);
		    
            if (headers) {
                for (key in headers) {
                    xhr.setRequestHeader(key, headers[key]); //Authorization
                }
            }

            //xhr.onload
            xhr.onreadystatechange = function (e) {
                  if(this.readyState == this.HEADERS_RECEIVED) {
                    //xio.log.debug('xhr.onreadystatechange HEADERS_RECEIVED')
                    //xio.log.debug(this.getAllResponseHeaders());
                  }
                
                if (this.readyState === 4) {
                    //xio.log.debug('xhr.readyState DONE',this.getAllResponseHeaders() )
                    d.resolve(
                        parseResult(xhr)
                    )

                }
            };
		    xhr.onerror = function (e) {
                d.reject(
                    parseResult(xhr)
                )
		    };
		    xhr.send(data);

		    return d.promise()   
        }
    }



	XioContext = function() {
		return this;
	};

    /*
    generalize to unit-oriented convertable value ?
    */
    XioValue = function(type,value,unit) {

        this.type = type
        this.value = value
        this.unit = unit
        
        this.converter = function(value,unit_from,unit_to) {
            if (type=='datetime') {
                if (unit_from=='TIMESTAMP') {
                    var date = new Date(value * 1000);
                    return date.toISOString()
                }

            }
            if (type=='amount') {
                var rates = {
                    'WEI': {
                        'ETH': 0.000000000000000001,
                    },
                    'ETH': {
                        'EUR': 560,
                    },
                    'EUR': {
                    }
                }
                rates['WEI']['EUR'] = rates['WEI']['ETH']*rates['ETH']['EUR']
                rates['EUR']['WEI'] = 1/rates['WEI']['EUR']
                rates['EUR']['ETH'] = 1/rates['ETH']['EUR']

                var unit_from = unit_from.toUpperCase()
                var unit_to = unit_to.toUpperCase()
                xio.log.debug('==> converter ',unit_from,unit_to)
                var rate = rates[unit_from][unit_to]
                xio.log.debug('==> rate 1 ',unit_from,'=',rate,unit_to)
                return value*rate
            }
            return '?'
        }
        this.convert = function (unit_to) {
            var value_to = this.converter(this.value,this.unit,unit_to)
            xio.log.info('==> convert',this.value,this.unit,unit_to,'=',value_to)
            return new XioValue(this.type,value_to,unit_to)    
        }

        // build label based on global context (eg: currncy for ammount)
        this.label = this.value+' '+this.unit    
        if (xio.context.currency && (this.unit!=xio.context.currency)) {
            
            var converted = this.convert(xio.context.currency)
            this.label = converted.value+' '+converted.unit    
        }

        return this
    }


	Xio = function() {
		return this;
	};
	Xio.prototype = {

		app: function(endpoint,context) { 
			return new XioApp(endpoint,context)
		},

        network: function(id,abi) { 
            return new XioNetwork(id,abi) // abi optional
        },
        client: function(endpoint,context) { 
            return new XioResource(endpoint,context)
        },
        user: function(private,seed,token) { 
            return new XioUser(private,seed,token)
        },

        request: function(method,path,data,headers,context) { 
            return new XioRequest(method,path,data,headers,context)
        },
        routes: function() {
            return new XioRoutes()
        },
        db: function(name) {
            return new XioDb(name)
        },
	}
	xio = new Xio();   
	xio.context = new XioContext()
    xio.handlers = new XioHandlers()
    xio.log = new XioLogger()
    xio._scheduler = new XioScheduler()
    xio.schedule = function(uid,t,handler) {
        return this._scheduler.put(uid,t,handler)
    }
    xio.tools = {
        md5: function() {
            var args = Array.prototype.slice.call(arguments);
            return Crypto.MD5(args.join(''));
        },
        parseQuery: function(path) {
            var params = {}
            if (!path)
                return params
        
            // var parsed = new URL(url)
            if (path.startsWith('?'))
                var query = path.slice(1)
            else
                var query = path

            var vars = query.split('&');
            for (var i = 0; i < vars.length; i++) {
                var pair = vars[i].split('=');
                var key = decodeURIComponent(pair[0]);
                var val = decodeURIComponent(pair[1]);
                params[key] = val
            } 
            return params
        },
        about: function(data) {
            //console.log('BEFORE XIO FIX ABOUT',data)
            //if (data['_fixed'])
            //    return data
            //data['_fixed'] = true

            if (!data['options']) {
                data['options'] = [] 
            }
            if (!data['methods']) {
                data['methods'] = {}
            }
            if (!data['name']) {
                data['name'] = '?' 
            }

            if (!data['about'])
                data['about'] = {}
            // fix des options

            if (data['methods']) {
                $.each(data['methods'],function(method,v) {
                    if (data['options'].indexOf(method) === -1) 
                        data['options'].push(method)
                })
            } 
            

            if (data['options'])
                data['options'].push('GET')
            /*
            var m = ['GET'] // 'ABOUT,'API',
            for (var i in m) {
                var method = m[i]
                console.log('OPTION -----------------',method,data)
                if (data['options'].indexOf(method) === -1)
                    data['options'].push(method)
            }
            */

            //var resource_methods = data['api']['/']
            //for (method in resource_methods)
            //    data['options'].push(method)

            // create api if missing
            /*
            if (!data['api'] || $.isEmptyObject(data['api'])) {
                data['api'] = {'/': {}} 
                
                $(data['options']).each( function(index,val) {
                    data['api']['/'][val] = {}
                })
            }
            if (data['methods']) {
                for (var method in data['methods']) {
                    data['api']['/'][method] = data['methods'][method]
                }
            }
            */

            // gestion resources
            if (data['resources']) {
                for (var childname in data['resources']) {
                    //data['api']['/'+childname] = {}
                }
            }
            /*
            // create routes
            var routes = []
            var basepath = basepath || ''
            for (var childpath in data['api']) {
                var methods = data['api'][childpath] || {}
                if (methods) {
                    for (var method in methods) {
                        var info = methods[method]
                        info['basepath'] = basepath
                        info['abspath'] = basepath+childpath // warning row['path'] pas fiable (eg: 825dbc86642d6d3085b36d5bb5fdce5b/screenshot)
                        info['relpath'] = childpath
                        info['method'] = method
                        routes.push(info)
                    }
                }
            }
            data['map'] = routes
            */


            //console.log('AFTER XIO FIX ABOUT',data)
            // fix bug doublbon
            data.options = $.unique(data.options)
            return data
        }

    }

    


    // handlers binding
    xio.handlers.bind('http',httpHandler)
    xio.handlers.bind('https',httpHandler)
    xio.handlers.bind('ws',websocketHandler)
    xio.handlers.bind('wss',websocketHandler)
 

})();



