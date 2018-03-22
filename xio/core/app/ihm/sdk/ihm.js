(function(){


    AppAmount = function(value,currency) {
        this.value = value
        this.currency = currency || 'wei'  
        this.label = this.value+' '+this.currency    
        this.convert = function (currency_to) {
            return new DxioAmount(this.value,currency_to)    
        }
        return this
    }



    AppLogger = function(app) {
        this._app = app    
        this.data = []
        this._log = function(level,msg) {
            console.log('['+level+']'+msg)
            this.data.push(
                {'level': level, 'msg': msg}
            )
        }
        this.info = function(msg) {
            this._log('INFO',msg)
        }
        this.debug = function(msg) {
            this._log('DEBUG',msg)
        }
        this.warning = function(msg) {
            this._log('WARNING',msg)
        }
        this.error = function(msg) {
            this._log('ERROR',msg)
        }
        return this
    }


    
    AppServices = function(app) {
        this._app = app    
        return this
    }
    AppServices.prototype.bind = function (name,config) {
        this._app.log.info('register service '+name)
        this._app.log.debug(config)
        if (this._app.inxio) {
            var handler = this._app.inxio.service(config)
            this[name] = handler
            this._app.log.debug(this[name])
        }

    }
      


    AppExts = function(app) {
        this._app = app    
        this._loading = {}
        return this
    }
    AppExts.prototype.load = function (name,callback) {
        if (!this[name] && !this._loading[name]) {
            this._app.log.info('loading extension '+name)
            this._loading[name] = true
            var basepath = this._app.nav.basepath+'sdk/ext/'+name+'/'
            var self = this
            $.getJSON( basepath+'about.json', function( data ) {
                self._loading[name] = data
                var nb_req = data.requirements.length
                var nb_loaded = 0
                var requirements = data.requirements

                console.log('...',name,requirements)
                
                var _load = function() {
                    if (requirements.length) {
                        var requirement = requirements.shift()
                        var reqpath = basepath+requirement
                        self._app.load(reqpath,function() {
                            nb_loaded += 1
                            console.log('loaded '+nb_loaded+'/'+nb_req+' ... '+name)
                            _load()
                        })
                    } else {
                        self[name] =  self._loading[name]
                        delete (self._loading[name])
                        self._app.log.info('loaded extension '+name)
                        self._app.publish('app.ext.'+name)  
                        if (callback) 
                            callback(self[name])
                    }
                }
                _load()
            }).fail( function(jqXHR, textStatus, errorThrown) { 
                self._app.log.error('loading extension '+name+' : '+textStatus) 
            })
        }
         
    }    


    AppRoutes = function(app) {
        this._app = app    
        this._routes = {}
        this._hooks = {}
        return this
    }
    AppRoutes.prototype.bind = function (path,handler) {
        this._routes[path] = {
            'handler': handler
        }
    }    
    AppRoutes.prototype.on = function (path,handler) {
        this._hooks[path] = handler
    }    
    AppRoutes.prototype.getHandler = function (path) {

        // routes declaré via app
        var routes = this._routes
        // routes du dom en cours
        $("page[path]").each( function() {
            routes[ $(this).attr('path') ] = {
                'target': $(this)
            }
        })
        $("section[path]").each( function() {
            routes[ $(this).attr('path') ] = {
                'target': $(this)
            }
        })
        console.log('getRouteHandler',path,routes)

        // quick check
        var handler = routes[path]
        if (handler) {
            var handler = routes[path]
            var params = {}
            var postpath = ''
            return [handler,params,postpath]
        }
        for (var route in routes) {
            //console.log('... route',route)
            var myRegexp = /(?:^|\s)format_(.*?)(?:\s|$)/g;

            var p = route.split('/')
            var pattern = []
            var urlparams = []
            for (var i in p) {
                var part = p[i]     
                if (part.charAt(0)==':') {
                    urlparams.push(part)
                    part = '([^\/]*?)'
                }
                pattern.push(part)
            }
            pattern = pattern.join('\/')
            pattern = '^'+pattern+'$'
            //console.log('... route',route,pattern)
            var rpattern = new RegExp(pattern,'gi')    
            var rmatch = rpattern.exec(path);
            //console.log('... route',route,pattern,params,rmatch)
            if (rmatch) {
                var handler = routes[route]
                var params = {}
                
                var rpattern = new RegExp(pattern,'gi') 
                var m = rpattern.exec(path)
                
                for (var i = 0; i < urlparams.length; i++) {
                    //console.log('... i',i,m[i+1])
                    params[urlparams[i]] = m[i+1]
                }
                params[urlparams[0]] = m[1]
                params[urlparams[1]] = m[2]
                params[urlparams[2]] = m[3]
                var postpath = ''
                //console.log(params)

                return [handler,params,postpath,route,this._hooks[route]] 
            }           
        }
        
    }

    AppNavLinks = function(app) {
        this._app = app    
        this.bind = function (name,config) {
            this._app.log.info('register link '+name)
            this[name] = config
        }
        return this
    }
    


    AppTags = function(app) {
        this._app = app    
        return this
    }

    AppTags.prototype.import = function (tagname) {
        var self = this
        var link = document.createElement('link');
        link.rel = 'import';
        link.href = tagname; //'tags/'+tagname+'.html';
        link.onload = function(e) { 
            self._app.log.info('imported tag '+tagname)
            console.log(link.import)
        };
        link.onerror = function(e) {
            self._app.log.error('unable to import tag '+tagname)
        };
        document.head.appendChild(link);
    } 
    AppTags.prototype.bind = function (tagname,handler) {

        //console.log('.... register tag '+tagname)    
        if (!this[tagname]) {
            this[tagname] = []    
        }
        this[tagname].push(handler)

        window.customElements.define(tagname,handler)
        /*
        if (typeof handler == 'string' || handler instanceof String) {   
            // ??
        } else if (handler instanceof Function) {
            
            var cls = class extends HTMLElement {
                constructor() {
                    super();
                }
                connectedCallback() {
                    this.innerHTML = handler(this)
                }
            }
           
        } else {
            cls = handler
        }
        window.customElements.define(tagname,cls)
        */
    }    



    Request = function(method,path,data,context) {
        this.method = method
        this.path = path
        this.data = data
        this.context = context
        return this
    }

	InxioApp = function(endpoint,handler) {

        var self = this

        // logs
        this.log = new AppLogger(this)

        // user
        this.user = null //new InxioUser(this)
        this.server = null

        this.handler = handler || '' 
        this.templates = { }
        this.cache = {}
        this._loaded = {}

        // ihm
        this._ready = false
        this.routes = new AppRoutes(this)
        this.tags = new AppTags(this)
        this.ext = new AppExts(this)
        this.services = new AppServices(this)
        this.contracts = {} 

        this._events = {
            'ready': []
        }
        this._routes = {
        }
        
        this.ihm = {
            'search': {
                'input': 'rr',
                'options': []     
            }      
        }    
        this.status =  {
            'message': 'App ready.'
        }

        // init nav

        var baseurl = document.location.origin
        var l = document.location.pathname.split('/');
        l.pop();
        var basepath = l.join('/')

        var hash = location.hash;
        if (hash) {
            var path = hash.slice(2)  
        } else {
            path = ''
        }
        this.device = {
            agent: navigator.userAgent,
            mobile: (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase())), 
            width: window.innerWidth,
            height: window.innerHeight
        }
        window.onresize = function() {  
            self.device.width = window.innerWidth
            self.device.height = window.innerHeight
        }

        this.nav = {
            basepath: basepath+'/',
            baseurl: baseurl+basepath,
            hashbang: '#!',
            location: location.hash,
            path: path,
            breadcrumb: [],
            sitemap: [],
            header: [],
            footer: [],
            page: {},   // current page ctrl
            links: new AppNavLinks(this),
            context: {
            },
            getPath: function (path) {
                path = path || ''
                if (path.charAt(0)!='/')
                    return this.hashbang+this.path+'/'+path
                else
                    return this.hashbang+path
            },
            parse: function (hash) {
                hash = hash || location.hash
                var info = hash.split('?')
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
                    'path': hash.slice(2),
                    'params': params
                }
            },
            setPath: function (path) {
                this.path = path
                this.breadcrumb = []
                var chref = this.hashbang
                var p = path.split('/')
                for (i in p) {
                    if (p[i]) {
                        chref = chref+'/'+p[i]
                        this.breadcrumb.push({
                            'name': p[i],
                            'href': chref
                        }) 
                    }


                }
            },
            setContext: function (key,val) {
                if (val!=undefined) {
                    this.context[key]= val;
                } else {
                    this.context = key;
                }

            },
            updateContext: function (context) {
                for(key in context) {
                    this.context[key] = context[key];
                }
            },
            goto: function (path) {
                //console.log('goto '+path)     
                var newpath = this.getPath(path)   
                location.hash = newpath
            },
        }

        this.init()
		return this
	}
    InxioApp.prototype.init = function () {

        this.log.info('init app')


        var self = this

        $(document).ready( function() {

            if (inxio_bootstrap) {
                // hide des pages
                self.log.info('dom ready')
                $('body').hide()
                $('*[path]:not([active])').hide()
            }

            // generation app.nav.pages pour header/footer dynamiques
            // a prendre dans about ou via dom ? ou les 2 ?
            $('nx-page').each( function() {

                var label = $(this).attr('label') || $(this).attr('path') 
                self.nav.sitemap.push({
                    'path': $(this).attr('path'),
                    'label': label
                }) 

            }) 
        })

        this.ready( function() {
            self.run()
        })

        // about app
        $.getJSON( this.nav.basepath+'about.json', function( data ) {
            
            self.about = data
            if (self.about.sitemap)
                self.nav.sitemap = self.about.sitemap.concat(self.about.sitemap)

            $.each(self.nav.sitemap, function( i,page ) { 
                var n = page.nav
                if (n=='footer') {
                    self.nav.footer.push(page)
                } else {
                    self.nav.header.push(page)            
                }
            })    

            // rendrering
            if (self.about.rendering) { 
                var engine = self.about.rendering.engine
            } else { 
                var engine = 'bootstrap'
            }

            self.about.requirements.push(engine)
            
            // load requirements
            var nb_requirements = self.about.requirements.length
            var nb_requirements_loaded = 0
            if (!nb_requirements) { 
                self.publish('ready')
                return    
            }
            $.each(self.about.requirements, function( i,name ) { 
                // TOFIX self.ext.load 
                // name is confuse : requirement could be file
                self.load(name, function() {
                    nb_requirements_loaded += 1
                    if (nb_requirements_loaded>=nb_requirements) {
                        self.publish('ready')
                    }     
                })
            }) 

        }).fail(function() { 
            console.log('warning ... about.json error')
            self.about = {
                'rendering': {}
            }
            // no about ... check app tag
            //alert($('app').html())
            var apptag = $('app').first()
            console.log(apptag)
            self.about.title = apptag.attr('title')
            self.about.rendering.engine = $('*[rendering]').attr('rendering')
            if (self.about.rendering.engine) {
                self.ext.load('rendering/'+self.about.rendering.engine, function() {
                    self.publish('ready')
                }) 
            } else {
                self.publish('ready')
            }

        });
    }
    InxioApp.prototype.run = function () {
        self.log.info('inxio run.')
        if (inxio_bootstrap) {
            self.log.info('start app')
            app.render()
            $('body').fadeIn(50)
        } 
    }

    InxioApp.prototype.load = function (src,callback) {

        var filename = src.split('/').pop()
        var info = filename.split('.')
        if (info.length==1) {
            var type='ext'
            var src = src.split('/').pop()
        } else {
            var type = info.pop()
        }

        console.log('loading ... '+src)

        if (!this._loaded[src]) {
            this._loaded[src] = {
                'status': 0,
                'callbacks': []
            }
            if (type=='ext') {
                var self = this
                // fix bad src which contain basepath of caller ext
                var src = src.split('/').pop()
                self.ext.load(src, function() {
                    console.log('LOADED '+src)
                    callback()
                })
            }
            else if (type=='js') {
                var head = document.getElementsByTagName('head')[0];
                var script = document.createElement('script');
                script.type = 'text/javascript';
                var self = this
                script.onload = function() {
                    console.log('LOADED '+src)
                    self._loaded[src].status = 200    
                    for (var i in self._loaded[src].callbacks) {
                        var h = self._loaded[src].callbacks[i]
                        h()
                    }
                }
                script.src = src;
                head.appendChild(script);

            }

            else if (type=='css') {
                var head = document.getElementsByTagName('head')[0];
                //document.write('<link rel="stylesheet" type="text/css" href="'+src+'"></link>');
                var link = document.createElement('link');
                link.type   = 'text/css';
                link.rel    = 'stylesheet';
                //link.onload = () => { resolve(); console.log('style has loaded'); };
                link.href   = src;
                head.appendChild(link);
                this._loaded[src].status = 200 
                for (var i in this._loaded[src].callbacks) {
                    var h = this._loaded[src].callbacks[i]
                    h()
                }
            }
            else if (type=='json') {
                $.getJSON( src, function( data ) {
                    callback(data)
                })
            }
            else if (type=='html') {
                var link = document.createElement('link');
                link.rel = 'import';
                link.href = src;
                var self = this
                link.onload = function(e) { 
                    console.log('LOADED '+src)
                    self._loaded[src].status = 200    
                    for (var i in self._loaded[src].callbacks) {
                        var h = self._loaded[src].callbacks[i]
                        h()
                    }
                };
                link.onerror = function(e) {
                    self.log.error('unable to load '+src)
                };
                document.head.appendChild(link);
            }
        }
        if (this._loaded[src].status==200) {
            callback()
        } else {
            this._loaded[src].callbacks.push(callback)
        }
    }


    InxioApp.prototype.template = function (template,data) {

        return this.templates[template]
    }



    InxioApp.prototype.login = function (seed,password) {
        // init user
        
        this.user = new InxioUser(null,seed)

        this.publish('user.loggedin')

        // init network
        var network = xio.network('0x1058aA85D3080AD9B0c107A05ff13013755e181D')

        console.log(network)

        xio.context.user = this.user
        xio.context.network = network

        // connect user to network
        //var cli = this.user.connect(network)

        return $.Deferred().resolve( this.user )
    }
    InxioApp.prototype.logout = function (callback) {
        this.publish('user.loggedout')
        return this.user.logout()

    }

    InxioApp.prototype.ready = function (callback) {
        if (this._ready) {
            callback()
        } else {
            this._events['ready'].push(callback)
        }
    }

    InxioApp.prototype.publish = function (topic,data) {
        console.log('publish '+topic,data)  
        for (i in this._events[topic]) {
            var callback = this._events[topic][i]
            callback(data) 
        }
    }
    InxioApp.prototype.subscribe = function (topic,callback) {
        console.log('subscribe '+topic,callback)
        if (!this._events[topic])
            this._events[topic] = []     
        this._events[topic].push(callback)
    }
    InxioApp.prototype.on = function (topic,callback) {
        console.log('on '+topic,callback) 
        if (!this._events[topic])
            this._events[topic] = []     
        this._events[topic].push(callback)
    }
    
    InxioApp.prototype.display = function (target,html) {
    
        console.log('display ',html)
        target = target || 'body'
        var element = angular.element(target)
        var html = element.html()

        alert(html)

        // post traitement
        var $ngtarget = $("[ng-app]");
        angular.element($ngtarget).injector().invoke(['$compile', function ($compile) {
            var $scope = angular.element($ngtarget).scope();
            var compiled = $compile('<test></test><test0></test0><test1></test1><test2></test2>')($scope)
            alert(compiled.html())
            angular.element(target).html(compiled)  
            //angular.element(target).empty().append(compiled)  
            $scope.$apply();
        }]);
        
    }

    InxioApp.prototype.render = function (path,data) {

        if (path==undefined) { 
            path = window.location.hash.slice(2)
        }
        console.log('====== render '+path) 
        console.log('====== render data',data) 
        this.log.info('rendering '+path)
        
        //console.log($scope.app.nav)

        this.status.message = 'render '+path
            
        if (!path) {
            path = window.location.hash.slice(2) || ''
        } else {
            //history.pushState(context, path, '#'+path);
        }    
        if (path.charAt(0)!='/')
            path = '/'+path

        // recherche handler (route ou element page du dom courant) pour le render 
        var route = this.routes.getHandler(path)
        if (!route) {
            return
            console.log('no route for '+path+' = ',route,'render FULL BODY')
            var data = {
                'app': this,
                'test': 'YEBO'
            }
            return $('body').render(data)
        }

        this.nav.setPath(path)
        this.nav.setContext(route[1])
        this.nav.updateContext(data)

        var el = route[0].target 
        console.log('====== render target',el) 

        el.siblings('section').hide()
        el.show()
        //this.nav.page = page
        $(el).attr('active','true').siblings('*[path]').removeAttr('active')

        var hook = route[4];
        if(hook) {
            hook()
        }
        return 
 
    }


})();


$(document).ready( function() {

    app = new InxioApp()

    app.tags.import('sdk/tags/app.html')
    app.tags.import('sdk/tags/onboarding.html')


})


class AppTag extends HTMLElement {

    constructor() {
        super();
    }

    connectedCallback() {
        this.innerHTML = this.render()
    }
}
    

$(window).bind( 'hashchange', function(e) { 
    var hash = location.hash
    if (hash.startsWith(app.nav.hashbang)) {
        var parsed = app.nav.parse(hash)
        app.render(parsed.path,parsed.params)    
    } else if (hash.startsWith('#.')) {
        path = app.nav.getPath( hash.slice(3) )   
        location.replace(path);
    }
});






$.fn.extend({

    render: function (data,template,debug) {
        // cas d'un element avec data-lab-template

        function _render(el,data,template,debug) {

            if (!el.xiotemplate) {
                if (template) 
                    el.xiotemplate = template 
                else
                    el.xiotemplate = $(el).html()   
            }

            var html = Mustache.to_html(el.xiotemplate,data);
            $(el).html(html)
        }

        var el = this[0]
        if (!el)
            console.log('template not found :'+template)
        if (el._template) {
            var html = Mustache.to_html(el._template,data);
            this.html(html)
            return
        }
        if (this.prop("tagName").toLowerCase()=='script') {
            var html = Mustache.to_html(this.text(),data);
            return html
        }
        if (this.prop("tagName").toLowerCase()=='template') {
            var html = Mustache.to_html(this.html(),data);
            return html
        }
        return this.each(function() {
            _render(this,data,template,debug)
            return this
        });
    },


    enhance: function () {


        /*
        $('*[data-item-action]').unbind('click').bind('click', function(event) { 
            var item_path = $(this).closest('.item').data('item-path')
            var item_action = $(this).data('item-action')
            if (item_action=='PIN') {
                pinResource(item_path)
            } else {
                showResourceRequest(item_path,item_action)
            }
        })
        */


    },

});





