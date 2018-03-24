(function(){

    var standard_method = ['GET','PUT','POST','PATCH','DELETE','HEAD']

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
					console.log('websocket connected to '+this.parent.url);
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
		        this.ws.onerror = function(e) { console.log('ERROR '+e); };
		        this.ws.onclose = function() { 
                    this.parent.connected = false; 
                    console.log('disconnected');

                };
		    } 
		}


		this.send = function(msg) {
            msg = JSON.stringify( msg);
		    //this.log('SEND >>> '+msg);
		    this.ws.send(msg);
		}

		this.log = function(msg) {
		    console.log('xiowebsocket '+this.url+' '+msg)
		}
		this.get = 	function(path,params,callback,errback,feedback) 	{ return this.request('GET',path,params,callback,errback,feedback) } 
		this.post = function(path,params,callback,errback,feedback) 	{ return this.request('POST',path,params,callback,errback,feedback) }

		this.request = function(method,path,params,headers,callback,errback,feedback) {

            if (!this.connected) {
                console.log('must reconnect for request')
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


			console.log('REQUEST '+method+' '+path+' '+params)
			//console.log(callback);
			//console.log(headers);
		    //callback()
		}
		return this
	}


    httpHandler = function(endpoint) {
        this._endpoint = endpoint

        this.request = function (method,path,params,headers,callback,errback,feedback) {
            // path doit etre absolut
            // resolve query in path
            var info = parseUrl(path)
            path = info.path
            params = params || info.query

            var path = this._endpoint+path  

            console.log('params',params)

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
                //console.log('HEADERS ??',xhr.getAllResponseHeaders() )
            
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


		    var url = path+'?'+params
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
                    //console.log('xhr.onreadystatechange HEADERS_RECEIVED')
                    //console.log(this.getAllResponseHeaders());
                  }
                
                if (this.readyState === 4) {
                    //console.log('xhr.readyState DONE',this.getAllResponseHeaders() )
                    if (callback) {
                        callback( parseResult(this) )
                    }

                }
            };
		    xhr.onerror = function (e) {
                console.log('xio xhr error',e)
                if (errback) {
                    errback( parseResult(xhr) )
                }
		    };
		    xhr.send(data);
		    return xhr   
        }
    }

	XioResource = function(app,path,method,method_params) {
        //console.log('CREATE RESOURCE FROM ...',method,path)
        this._app = app
        this._method = method
        this._method_params = method_params
        this._path = path
        this._status = 0
        this._content = null
        this._spool = []

        if (method) {
            this._status = 0 // waiting parent 
        } else {
            this._status = 200
        }
        return this
    }
	XioResource.prototype = {
        get: function(path,query) { return this.then('GET',path,query) },
        put: function(path,data) { return this.then('PUT',path,data) },
        post: function(path,data) { return this.then('POST',path,data) },
        delete: function(path) { return this.then('DELETE',path) },
        patch: function(path,data) { return this.then('PATCH',path,data) },
        about: function(path,params) { return this.then('ABOUT',path) },
        api: function(path,params) { return this.then('API',path) },
        connect: function(path,params) { return this.then('CONNECT',path,params) },
        subscribe: function(path,data) { return this.then('SUBSCRIBE',path,data) },
        debug: function() { 
            console.log('=====DEBUG====',this._path)
            console.log(this)
         },
        feedback: function(callback) {
            
        },
        then: function(method) { //,path,query
            //console.log(arguments)

            if (typeof method === "function") {
                // lambda method
                var query = method
                var method = '__lambda__'

            } else {
                // standard method
                var path = arguments[1]
                var query = arguments[2]
            }
            /*
            else if (standard_method.indexOf(method)<0) {
                // custom method
                var path = arguments[1]
                var query = arguments[2]

                if (typeof param1==='object') {
                    var query = param1
                } else {
                    var query = {}
                    for (i=1; i<arguments.length; i++) {
                        query['_'+(i-1)] = arguments[i]
                    }
                }

            } else {
                // standard method
                var path = arguments[1]
                var query = arguments[2]
            }
            */



            var r = new XioResource(this._app,path,method,query)

            if (this._status==200 || this._status==201) {
                // do it
                if (r._path) {
                    if (this._path) {
                        r._path = this._path+'/'+r._path
                    }
                } else {
                    r._path = this._path
                }
                r.execute()
            } else {
                // or spool it -> chain flow
                this._spool.push(r)
            }
            return r
        },
        _onSucceed: function(data) {

            this._status = data['status']   
            this._content = data['content']  
            // check CONNECT && TOKEN

            // check 201
            if (data['status']==201) {
                newpath = data['headers']['Location']
                if (newpath) {
                    this._path = newpath   
                } 
            }

            for (i in this._spool) {
                var r = this._spool[i]

                // mise a jour du path (cas des 201)
                if (r._path) {
                    r._path = this._path+'/'+r._path
                } else {
                    r._path = this._path
                }
                r.execute( this._content )
                
            }
        },
        execute: function( currentresult ) {

            var self = this // pb avec le this du callback 
            if (this._method=='__lambda__') {

                var result = this._method_params(currentresult)

                var resp = {
                    'status': 200,
                    'content':result
                }
                this._onSucceed(resp)
            } else {
                var callback = errback = function (resp) { self._onSucceed(resp) }
                var req = this._app.request(this._method,this._path,this._method_params, callback, errback,null)
            }
            return this
        },
    }

	XioApp = function(endpoint,params) {
        params = params || {}
        console.log('create xio app to '+endpoint+'...')
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
            console.log('unknow handler', endpoint)
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
            //console.log('app request',method,path,query)
            //console.log('app token',this._token)
            if (this._basepath && this._basepath.slice(-1)!='/' && path && path[0]!='/')
                path = this._basepath+'/'+path
            else if (this._basepath && this._basepath.slice(-1)=='/' && path && path[0]=='/')
                path = this._basepath+path.slice(1)
            else
                path = this._basepath+path
            //console.log('app request',method,path,query)
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

	XioContext = function() {
		return this;
	};


	Xio = function() {
		return this;
	};
	Xio.prototype = {

		app: function(endpoint,config) { 
			return new XioApp(String(endpoint),config)
		},


        network: function(id) { 
            return new XioNetwork(id)
        },

        user: function(private,seed,token) { 
            return new XioUser(private,seed,token)
        },

	}
	xio = new Xio();   
	xio.context = new XioContext()

})();



