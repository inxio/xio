(function(){
    

    AppExts = function(app) {
        this._app = app    
        this._loading = {}
        this._basesrc = xio_sdk_baseurl+'/ext/'
        this._basesrc_component = xio_sdk_baseurl+'/components/'
        return this
    }
    AppExts.prototype._loadRequirements = function (basesrc, name, callback) {
        var self = this
        var data = self[name] || {}

        var requirements = data.requirements || []
        var nb_loaded = 0
        var nb_req = requirements.length

        var _load = function() {
            if (requirements.length) {
                var requirement = requirements.shift()
                var reqpath = basesrc+requirement
                self._app.load(reqpath,function() {
                    nb_loaded += 1
                    _load()
                })
            } else {
                self[name] =  self._loading[name]
                delete (self._loading[name])
                self._app.log.debug('loaded extension '+name)
                self._app.publish('app.ext.'+name)  
                if (callback) 
                    callback(self[name])
            }
        }
        _load()

    }
    AppExts.prototype.loadExt = function (name,callback) {
        var self = this
        if (!this[name] && !this._loading[name]) {

            xio.log.info('loading extension '+name)
            this._loading[name] = true

            var basesrc = this._basesrc+name+'/'
            $.getJSON( basesrc+'about.json', function( data ) {
                self[name] = data
                self._loadRequirements(basesrc,name,callback)
            }).fail( function(jqXHR, textStatus, errorThrown) { 
                self._app.log.error('loading extension '+name+' : '+textStatus) 
            })
        }
         
    }    
    AppExts.prototype.loadComponent = function (name,callback) {
        var self = this
        if (!this[name] && !this._loading[name]) {

            xio.log.info('loading component '+name)
            this._loading[name] = true

            var basesrc = this._basesrc_component+name+'/'
            var reqpath = basesrc+name+'.js'

            self._app.load(reqpath,function() {
                self._loadRequirements(basesrc,name,callback)
            })
        }
    } 


	XioUi = function(endpoint,handler) {

        var self = this

        // global data
        this.data = {}
        this.data.i18n = {}

        this.dev = false
        this.debug = false

        // logs
        this.log = xio.log
        this.log.level = null

        // user
        this.user = null 
        this.server = xio.app()
        this.handler = handler || '' 
        this.templates = { 
            load: function(path) {
                return $.get( self.nav.basepath+path)
            }
        }
        this.cache = {}
        this._loaded = {}
        
        // ihm
        this._ready = false
        this.ext = new AppExts(this)
        //this.tags = new AppTags(this)
        //this.templates = new AppTemplates(this)
        //this.services = new AppServices(this)
        this.routes = new xio.routes()
        this.contracts = {} 

        this._events = {
            'ready': []
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
        this.layout = {
            slot: {}
        }
        this.nav = {
            basepath: basepath+'/',
            baseurl: baseurl+basepath,
            hashbang: '#!',
            location: location.hash,
            landing: '#home',
            language: 'fr',
            path: path,
            breadcrumb: [],
            request: {},
            sitemap: [],
            header: [],
            footer: [],
            page: {},   // current page ctrl
            //links: new AppNavLinks(this),
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
                if (hash.startsWith(this.hashbang)) {
                    path = hash.slice(2)
                } else {
                    path = hash.slice(1)
                }
                return {
                    'path': path,
                    'query': params
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
                $('xio-breadcrumb').render(this.breadcrumb)
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
                var newpath = this.getPath(path)   
                location.hash = newpath
            },
        }

		return this
	}
    XioUi.prototype.init = function () {

        var self = this
        this.log.info('init app')

        // capture body
        //this.body = $('body')

        this.root = $('xio-app').first() // xio-app
        
        if (!this.root) {
            this.root = $('body').find('.xio-element').first()
        }
        this.root.hide()
        //this.body = $('body').clone()
        //$('body').html('<div style="display: table; width:100%; height:100%"><div style="display: table-cell; vertical-align: middle; "><div style="width:40%; margin-left: auto; margin-right: auto;text-align: center">loading ...</div></div></div>')


        // globals templates
        /*
        var d1 = self.load( this.nav.basepath+'sdk/core/templates.html', function(  ) {
            self.log.info('templates loaded')
        })
        */

        // about app

        var global_requirements = [
            'sdk/components/app',
            'sdk/components/input',
            'sdk/components/resource',
            'sdk/components/onboarding',
            'ethereum',
            'bootstrap'
        ]

        var d2 = $.getJSON( this.nav.basepath+'about.json').then( function( data ) {
            
            var d = $.Deferred(); 
            self.about = data || {'requirements':[]}

            if (self.about.sitemap) {
                self.nav.sitemap = self.about.sitemap //.concat(self.about.sitemap) // pb doublon concat 
            }

            // global reqs

            $.each(global_requirements, function( i,src ) { 
                self.about.requirements.push(src)
            }) 
            
            
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
                        d.resolve(true)
                    }     
                })
            }) 

            // init nav & layout data
            $.each(self.nav.sitemap, function( i,page ) { 
                var slot = page.slot || 'header'
                var slots = slot.split(' ')
                for (var i in slot) {
                    slot = slots[i]
                    if (!self.layout.slot[slot]) {
                        self.layout.slot[slot] = {}
                    } 
                    if (!self.layout.slot[slot]['links']) {
                        self.layout.slot[slot]['links'] = []
                    } 
                    self.layout.slot[slot]['links'].push(page) 
                }
           
            })    
            
            return d.promise()

        })

        
        return $.when( d2).always(function (r2) {
            // init user
            try {
                XioUser.loadSession()
                self.user = xio.context.user

                // init server
                if (xio.context.server)
                    self.server = xio.context.server // overwrite default server
                var endpoint = document.location.origin
                
                // init connection
                if (self.user && endpoint) {
                    self.user.connect(endpoint).then(function(server) {
                        self.server = server
                    })
                }
            } catch(e) {
                console.log(e)
                self.log.error(e)
            }
            self.log.info('APP READY.')
            self.publish('ready')
            self.run()
        })



    }
    XioUi.prototype.run = function (path) {

        console.log('RUN',this.root)

        var self = this

        path = path || null
        
        this.log.info('RUN '+path)
        this.log.info('APP RUN. ',this.root)

        // prop
        this.prop('dev', this.dev)
        this.prop('debug', this.debug)
        this.prop('mobile', this.device.mobile)
        this.prop('user', (this.user && this.user.id) )


        // render
        
        var data = {
            'app': this,
            '_': this.data.i18n[this.nav.language]
        }

        return this.root.render(data).then(function() {

            self.root.show()

            if (!path) {
                if (window.location.hash) {
                    path = window.location.hash
                } else {
                    path = app.nav.landing || this.root.children('xio-page').first().attr('id')
                } 
            } 
            console.log('RUN SHOW ',path)
            self.render(path)

        })
    }
    XioUi.prototype.redirect = function (href) {
        var newhref = window.location.href.split('#')[0]+href
        if (newhref!=window.location.href)
            window.location.href = newhref
        else
            app.run(href)

    }
    XioUi.prototype.uuid = function () {
        var dt = new Date().getTime();
        var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = (dt + Math.random()*16)%16 | 0;
            dt = Math.floor(dt/16);
            return (c=='x' ? r :(r&0x3|0x8)).toString(16);
        });
        return uuid;
    }
    XioUi.prototype.bind = function (path,handler) {
        this.routes.bind(path,handler)
    }
    XioUi.prototype.schedule = function (id,t,handler) {
        xio.schedule(id,t,handler)
    }
    XioUi.prototype.enhance = function (el) {
        
        var self = this

        // handle relative link
        $(el).find("a[href^='#./']").click(function(e) {
            e.preventDefault()
            try {
                //$(this).addClass('active')

                var element = $(el).closest('xio-resource')[0]
                //var req = xio.request('GET',$(this).attr('href').slice(3))
                var method = $(this).attr('href').slice(4).toUpperCase()
                var req = xio.request(method)
                element.render( req )
            } catch(error) {
                console.log(error);
            }
            return false;
        })

        // handle form
        $(el).find('form').submit(function(e) {
            e.preventDefault();
            try {
                alert('??form')
                var form = $(this);
                var method = form.data('xio-method') || 'POST'
                var path = form.data('xio-path') || ''
                var callback = form.data('xio-callback')
                var payload = { };
                $.each( form.serializeArray(), function() {
                    payload[this.name] = this.value;
                }); 
                // get first resource ?
                var nxelement = $(this).closest('.xio-resource')
                var nxresource = nxelement[0]

                var req = xio.request(method,path,payload,{},{'submited':true})
                return nxresource.render(req)

                alert('SUBMIT '+method+' to '+nxresource.nodeName)
                var d = nxresource.render(req)
                if (callback) {
                    d.then( function(resp) {
                        console.log(nxresource)
                        return nxresource[callback](resp)
                    })
                }
                return d;
            } catch(error) {
                console.log(error);
            }
            return false;
        })

        // handle multi submit
        $(el).find('form button[data-xio-method]').click(function() { 
            var method = $(this).data('xio-method')
            $(this).closest('form').data('xio-method',method).submit()
        })
    }
    XioUi.prototype.prop = function (key,value) {
        if (value==undefined)
            return $('body').hasClass('xio-'+key)
        if (value)
            $('body').addClass('xio-'+key)
        else
            $('body').removeClass('xio-'+key)
    }
    XioUi.prototype.login = function (seed,password,endpoint) {
        // init user
        console.log('LOGIN', seed,password,endpoint)
        var self = this
        return XioUser.login(null,seed).then(function(user) {
            self.user = user
            return self.user.connect( endpoint ).then(function(server) {
                self.server = server
                self.run()
            })
        })
    }

    XioUi.prototype.logout = function (callback) {
        this.user.logout()
        this.prop('user', false )
        this.run('#')
    }

    XioUi.prototype.load = function (src,callback) {
        var self = this

        var filename = src.split('/').pop()
        var info = filename.split('.')
        if (info.length==1) {
            if (src.startsWith('sdk/components')) {
                var type='component'
                var src = src.split('/').pop()
            } else {
                var type='ext'
                var src = src.split('/').pop()
            }
        } else {
            var type = info.pop()
        }

        this.log.info('loading ... '+src)


        // fix new version
        if (type=='html') {
            if (!this._loaded[src]) {
                return this._loaded[src] = $.get( src ).then( function(content) {
                    if (callback)
                        callback(content)
                    return content
                })
            }
            return this._loaded[src]
        }

        if (!this._loaded[src]) {
            this._loaded[src] = {
                'status': 0,
                'callbacks': []
            }
            if (type=='ext') {
                var self = this
                // fix bad src which contain basepath of caller ext
                var src = src.split('/').pop()
                self.ext.loadExt(src, function() {
                    self.log.info('LOADED '+src)
                    callback()
                })
            }
            else if (type=='component') {
                var self = this
                // fix bad src which contain basepath of caller ext
                var src = src.split('/').pop()
                self.ext.loadComponent(src, function() {
                    self.log.info('LOADED '+src)
                    callback()
                })
            }
            else if (type=='js') {
                var head = document.getElementsByTagName('head')[0];
                var script = document.createElement('script');
                script.type = 'text/javascript';
                var self = this
                script.onload = function() {
                    self.log.debug('LOADED '+src)
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
                var link = document.createElement('link');
                link.type   = 'text/css';
                link.rel    = 'stylesheet';
                //link.onload = () => { resolve(); app.log.info('style has loaded'); };
                link.href   = src;
                head.appendChild(link);
                this._loaded[src].status = 200 
                for (var i in this._loaded[src].callbacks) {
                    var h = this._loaded[src].callbacks[i]
                    h()
                }
            }
            else if (type=='json') {
                return $.getJSON( src ).then( function(content) {
                    self._loaded[src].status = 200
                    self._loaded[src].content = content
                    if (callback)
                        callback(content)
                    return content
                })
            }
            else if (type=='html') {
                //alert(src)
                return $.get( src ).then( function(content) {
                    //alert('loaded '+content)
                    self._loaded[src].status = 200
                    self._loaded[src].content = content
                    if (callback)
                        callback(content)
                    return content
                })
            }
            /*
            // html import disabled from polyfil
            else if (type=='html') {
                var link = document.createElement('link');
                link.rel = 'import';
                link.href = src;
                var self = this
                link.onload = function(e) { 
                    self.log.info('LOADED '+src)
                    $(this.import).find('template[id]').each( function() {
                        var id = $(this).attr('id');
                        self.templates[id] = this
                    })
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
            */
        }
        if (this._loaded[src].status==200) {
            if (callback) {
                callback(self._loaded[src].content)
            }
            else {
                var d =  $.Deferred(); 
                d.resolve(self._loaded[src].content)
                return d.promise()
            }
        } else if (callback) {
            this._loaded[src].callbacks.push(callback)
        }
        else {
            var d =  $.Deferred(); 
            this._loaded[src].callbacks.push( function(content) {
                d.resolve(content)
            })
            return d.promise()
        }
    }

    XioUi.prototype.scroll = function (target) {
        $('body,html').animate(
            {'scrollTop':target.offset().top - 90},
            900
        );
    }

    XioUi.prototype.template = function (template,data) {
        return this.templates[template]
    }


    XioUi.prototype.ready = function (callback) {
        if (this._ready) {
            callback()
        } else {
            this._events['ready'].push(callback)
        }
    }

    XioUi.prototype.publish = function (topic,data) {
        this.log.debug('publish '+topic,data)  
        for (i in this._events[topic]) {
            try {
                var callback = this._events[topic][i]
                callback(data) 
            } catch(error) {
                this.log.error(error);
            }

        }
    }
    XioUi.prototype.subscribe = function (topic,callback) {
        this.log.debug('subscribe '+topic,callback)
        if (!this._events[topic])
            this._events[topic] = []     
        this._events[topic].push(callback)
    }
    XioUi.prototype.on = function (topic,callback) {
        this.log.debug('on '+topic,callback) 
        if (!this._events[topic])
            this._events[topic] = []     
        this._events[topic].push(callback)
    }

    XioUi.prototype.renderFallback = function (path,data) {
        // born to be overwrited
        // if hash try #home to /home
        if (path.startsWith('#'))
            return this.render('/'+path.slice(1))
        
    }
    XioUi.prototype.confirm = function (config) {
        alert('confirm '+config.title)
        var d = $.Deferred(); 

        //var template = doc.querySelector('#template-transaction-confirmation');
        //var html = $(template).render({})
        //$('#appmodal').html(html)
        /*
        try {
            if (config.title)
                $('#appmodal .modal-title').text(config.title)
            if (config.description)
                $('#appmodal .modal-body p.description').html(config.description)
            if (config.amount)
                $('#appmodal .modal-body p.amount').html(config.amount.label)
            
            $('#modalCancel').unbind().click(function() {
                d.reject(false);
            })
            $('#modalConfirm').unbind().click(function() {
                $('#appmodal').modal('hide');
                d.resolve(true);
            })

            $('#appmodal').modal('show')
            alert($('#appmodal'))
        } catch(e) {
            alert(e)
            d.resolve(true);
        }
        */
        d.resolve(true);
        return d.promise()
        
    }
    XioUi.prototype.render = function (path,data) {

        var self = this
        this.log.info('====== APP RENDER '+path,data) 

        if (path.startsWith('#')) {
            var parsed = app.nav.parse(path)
            path = parsed.path
            data = parsed.query 
        } else if (path.startsWith('#.')) {
            path = app.nav.getPath( path.slice(3) )   
            location.replace(path);
        } 

        this.log.info('====== APP RENDER '+path,data) 

        this.nav.setPath(path)

        // handle language
        if (!path && data.lang) {
            app.nav.language = data.lang
            app.run('#')
            return true;
        }

        // step1 : find element
        var el = $('#'+path.split('/')[0])
        console.log(el)
        
        // step2 : custom handler (post rendering before show)
        var route = this.routes.getHandler(path)
        if (route) {
            if (el.length) {
                el.render().then(function() {
                    try {
                        result = route.handler(data)
                        return $.when(result).then(function(data) {
                            self.show(el)
                        })
                    } catch(e) {
                        console.log('DATA ERROR',e)
                        return
                    }
                })
            } else {
                result = route.handler(data)
                return $.when(result).then(function(data) {
                    self.show(el)
                })
            }
        } 

        // default handling

        return $.when(data).then(function(data) {
            console.log('RENDER ELEM = ',el)
            console.log('RENDER DATA = ',data)
            return el.render(data)
        })
    }


})();




window.app = new XioUi()

$(document).ready( function() {
    app.init()
})

$(window).bind( 'hashchange', function(e) { 
    console.log('hashchange ...', location.hash)
    var hash = location.hash
    app.render(hash)
});




$.fn.extend({


    render: function (data,template,debug) {

        var el = this[0]

        // cas des xio-elements 
        if (el && el.render) {
            return el.render(data)
        }

        /*
        else {
            // to remove ???
            // custom tag -> call element render for rebuild it
            //if (el.render)
            //    return el.render() 
        }
        */

        //app.log.info('.................... applyTemplate')
        var id = this.attr('id')
        // auto register template
        if (!template && id && !app.templates[id]) {
            
            if (id) {
                // lookup template
                var tpl = this.children('template').first()
                if (tpl) {
                    app.templates[id] = tpl
                    this.html()
                }
            }
        }


        function applyTemplate(tpl,data) {

            // prevent sub template rendering
            var subtpl = false
            var $tpl = $("<root/>")
            $tpl.html(tpl)
            $tpl.find('template').each(function() {
                this.innerHTML = this.innerHTML.replace(/{{/g, "((").replace(/}}/g, "))")
                subtpl = true
            })

            var html = Mustache.to_html( $tpl.html() ,data);
            if (subtpl) {
                html = html.replace(/\(\(/g, "{{").replace(/\)\)/g, "}}")
            }
            
            return html
        }
        

        function _render(el,data,template,debug) {

            if (!el.xiotemplate) {
                if (template) 
                    el.xiotemplate = template 
                else
                    el.xiotemplate = $(el).html()   
            }

            var html = applyTemplate(el.xiotemplate,data) //Mustache.to_html(el.xiotemplate,data);
            $(el).html(html)
        }

        //console.log('render',this,data,el)

        if (!el) {
            //app.log.info('template not found :',this)
            return 
        }

        /*
        // to remove 
        else if (id && app.templates[id]) {
             console.log('id',id,app.templates[id])
            var tpl = app.templates[id].html()
            var html = applyTemplate(tpl,data)
            this.html(html)
            return this
        }
        */

        if (el._template) {

            //var html = Mustache.to_html(el._template,data);
            var html = applyTemplate(el._template,data)
            this.html(html)
            return
        }
        if (this.prop("tagName").toLowerCase()=='script') {
            // script -> return html
            //var html = Mustache.to_html(this.text(),data);
            //return html
            return applyTemplate(this.text(),data)
        }
        else if (this.prop("tagName").toLowerCase()=='template') {
            // template -> return html
            //var html = Mustache.to_html(this.html(),data);
            return applyTemplate(this.html(),data)
        } 
        
        return this.each(function() {
            _render(this,data,template,debug)
            return this
        });
    },


    enhance: function () {
        /*
        post rendering globals actions
        */
        app.enhance(this)
        return this
    },

});


/////// tools

function json2html(data) {
    var html = '';

    if (Array.isArray(data)) {
        html += '<table class="table  table-sm">';
        for (i in data) {
            var value = data[i];
            if (value) {
                html += '<tr>';
                html += '<td>'+json2html(data[i])+'</td>';
                html += '</tr>';
            }
        }
        html += '</table>';
    } else if (typeof data==="object" ) {
        html += '<table class="table  table-sm">';
        for (i in data) {
            var value = data[i];
            if (value) {
                html += '<tr>';
                html += '<th valign="top">'+i+'</th>';
                html += '<td>'+json2html(data[i])+'</td>';
                html += '</tr>';
            }
        }
        html += '</table>';
    } else {
        html = data;
    }
    return html;
}




