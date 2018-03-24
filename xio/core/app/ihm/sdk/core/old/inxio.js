(function(){

    App.prototype.onLoadStart = function () { console.log('load start') }
    App.prototype.onLoadStop = function () { console.log('load stop') }
    App.prototype.onLoggedIn = function () { console.log('logged in') }
    App.prototype.onLoggedOut = function () { console.log('logged out') }
    App.prototype.onShow = function (hash) { console.log('show '+hash) }

    App.prototype.init = function () {
        //this.session = JSON.parse(sessionStorage.getItem('session')) || {}
        // SESSION STORAGE pas compatible module chrome
        this.session = JSON.parse(localStorage.getItem('session')) || {}
        console.log('FOUND SESSION', this.session)
        this._token = this.session['token']
        $('body').addClass('inxio-user-logged')
        if (this.session) {
            this.onLoggedIn(this.session)
        }

    }

    App.prototype.applyTemplate = function (id_template,data,id_target) {
        var template = $('#'+id_template).html()
        var html = Mustache.to_html(template,data);
        if (id_target) {    
            $('#'+id_target).html(html)
        } else {
            return html
        }
    }


    App.prototype.login = function (login,password) {
        self = this
        //this.logout()
        return this.connect('',{'login': login, 'password':password}).then(
            function( data ) {
                var id = data['id']
                var token = data['token']
                data['login'] = login
                if (token) { 
                    console.log('USER LOGGED IN ...'+' '+JSON.stringify(data));
                    document.cookie = "token="+data['token'];
                    localStorage.setItem('session', JSON.stringify(data));
                    self.session = data
                    self._token = data['token']
                    self.onLoggedIn(data)
                    $('body').addClass('inxio-user-logged')
                } else {
                    console.log('AUTH FAIL ...'+' '+data);
                    if (onfailed) 
                        onfailed()
                }
                return data
            }
        )
    }

    App.prototype.logout = function () {
        localStorage.clear()
        document.cookie.split(";").forEach(function(c) { document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); });
        this.onLoggedOut()
        $('body').removeClass('inxio-user-logged')
    }

    App.prototype.show = function (hash) {
        if (hash==location.hash) // already in history,
            this.onShow(hash)
        else
            location.hash = hash // onshow via trigger
        
    }



    App.prototype.getResources = function (path,query) {
        console.log('==========> getResources',path,query)
        var self = this
        var path = path || ''
        var query = query || ''
        this.onLoadStart()
        return this.get(path,query).then(
            function (data) { 
                self.onLoadStop()

                $(data).each(function() {
                    self.fixData(this,path)
                })

                if (self.debug) {
                    console.log(data)
                    data['debug'] = json2html(data)
                }
                return data
            }
        )  
    }

    App.prototype.getUserResources = function (path,type) {
        console.log('==========> getUserResources',path,query)
        var self = this
        var path = path || ''
        var query = {}
        query['related'] = path
        query['type'] = type
        this.onLoadStart()
        return this.get('user/resources',query).then(
            function (data) { 
                self.onLoadStop()
                $(data).each(function() {
                    self.fixData(this,path)
                })
                if (self.debug) {
                    console.log(data)
                    data['debug'] = json2html(data)
                }
                
                return data
            }
        )  
    }



    App.prototype.aboutResource = function (path) {
        console.log('==========> aboutResources',path)
        var self = this
        var path = path || ''
        this.onLoadStart()
        return this.about(path).then(
            function (data) { 
                self.onLoadStop()

              
                data['ihm:api'] = self.fixApi( data['api']  , path)    

                data['ihm:editable'] = (data['@type']=='profile' || data['@type']=='shortcut')

                // fix des options
                data['options'] = ['ABOUT','API','STATS','TEST']
                var resource_methods = data['api']['/']
                for (method in resource_methods)
                    data['options'].push(method)
                    
                if (self.debug) {
                    console.log('======= API')
                    console.log(data['api'])
                    console.log(data['ihm:api'])
                }

                if (self.debug) {
                    console.log(data)
                    data['debug'] = json2html(data)
                }
                return data
            }
        )  
    }

    App.prototype.fixData = function (data,basepath) {
        var basepath = basepath || ''
        if (data['@id'])
            var id = data['@id']
        else
            var id = data['name']
        if (basepath)
            data['@id'] = basepath+'/'+id 
        else
            data['@id'] = id  
        return data
    }

    App.prototype.fixApi = function (api,basepath) {
        var routes = []
        var basepath = basepath || ''
        for (var childpath in api) {
            var methods = api[childpath]
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
        return routes
    }




    App.prototype.getResourceRequest = function (path,method) {
        console.log('==========> getResourceRequest',path)
        var self = this

        var ori_action = method // bug, on perd action dans la method ci dessous
        this.onLoadStart()
        return app.aboutResource(path).then( function (about) {
            self.onLoadStop()
            var data = {}
            var api = about['api']
            var config = api['/'][method] || {}
            
            console.log('==========> getResourceRequest API', method)
            console.log(api)
            console.log(config)
            
            /* ckwa ?
            // fix "METHOD :PATH"
            var nfo = action.split(' ')
            action = nfo[0]
            var postpath = nfo[1]
            if (postpath)
                path = path+'/'+postpath
            */

            // gestion urlparams
            var url_input = []
            var p = path.split('/')
            $(p).each( function(index,val) {
                if (val.startsWith(':')) {
                    url_input.push( {'name': val} )
                } 
            })
            data['ihm:urlinput'] = url_input
            data['path'] = path
            data['method'] = method
            data['input'] = config['input'] 

            console.log(data)

            var input_params = []

            if (data['input'] && data['input']['params']) {
                $(data['input']['params']).each( function(index,val) {
                    var name = val['name']
                    if (name.startsWith(':')) {
                        //data['ihm:urlinput'] = val    
                    } else {
                        // pb avec value car disparait du formulaire si existe (cas d'une op a moitié configuré coté serveur, dans ce cas ca doit disparaitre de la liste des input de about !)
                        //if (val['default']) data['input']['params'][index]['value'] = val['default']    
                        if (val['type'])
                            val['ihm_type_'+val['type']] = true    
                        else
                            val['ihm_type_text'] = true   

                        if (about['data'] && about['data'][val['name']]) {
                            val['value'] = about['data'][val['name']]       
                        }  
                        input_params.push(val)      
                    } 

                
                })
                data['input']['params'] = input_params
            }
            return data
        })
    }

    App.prototype.getResourceResponse = function (path,method,payload,callback) {

        var payload = payload || {};
        var _payload = { };
        for (var name in payload) {
            if (name.startsWith(':')) {
                var value = payload[name]
                path = path.replace(name, value);
            } else {
                _payload[name] = payload[name];
            }
        }; 

        if (payload['__body__']) {
            payload = payload['__body__']    
        }

        return app.request(method,path,_payload,function(resp) {
            console.log(resp['headers'])
            console.log(resp)

            //fix des headers
            resp['ihm'] = {}
            resp['ihm']['fromcache'] = resp['headers']['xio_cache_ttl']
            resp['ihm']['content_type'] = resp['headers']['Content-Type']

            headers = []
            for (var k in resp['headers']) {
                headers.push({'name': k, 'value': resp['headers'][k]})    
            }
            resp['headers'] = headers

            if (typeof resp['content'] != 'string')
                resp['content'] = JSON.stringify(resp['content'] , undefined, 4);

            callback( resp )

        })

    }



    function _render(el,data,template,debug) {

        if (!el.xiotemplate) {
            if (template) 
                el.xiotemplate = template 
            else
                el.xiotemplate = $(el).html()   
            if (debug)
                console.log('register template',el.xiotemplate) 
        }

        var html = Mustache.to_html(el.xiotemplate,data);
        
        if (debug) {
            console.log('apply template') 
            console.log('template src',el.xiotemplate)
            console.log('template data',data)
            console.log('template result',html)
        }
        $(el).html(html)
    }


	inxio = function(endpoint) {

        var endpoint = endpoint || window.location.protocol + "//" + window.location.host

        console.log('INIT INXIO '+endpoint)
		var app = xio.app(endpoint)
        app.init()
        app.cache = {}
        return app
	};


})();

$(document).ready( function() {

    $(window).bind( 'hashchange', function(e) { 
        var hash = location.hash;
        //var target = hash.substring(1)
        app.onShow(hash)
    });



})


/////// extend

$.fn.extend({

    render: function (data,template,debug) {
        // cas d'un element avec data-lab-template
        var el = this[0]
        if (!el)
            console.log('template not found :'+template)
        if (el._template) {
            console.log(data)
            //console.log(el._template)
            var html = Mustache.to_html(el._template,data);
            //console.log(html)
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



        $('*[data-item-action]').unbind('click').bind('click', function(event) { 
            var item_path = $(this).closest('.item').data('item-path')
            var item_action = $(this).data('item-action')
            if (item_action=='PIN') {
                pinResource(item_path)
            } else {
                showResourceRequest(item_path,item_action)
            }
        })


        $(this).find('a[data-user-path]').unbind('click').bind('click', function(event) { 
            $(this).closest('.isocontainer').nextAll().remove()
            selectItem( $(this).closest('.item') )
            showUserResource( $(this).data('user-path') )
        })

        $(this).find('a[data-item-path]').unbind('click').bind('click', function(event) { 
            $('#rootcontainer').children().remove()
            showResources( $(this).data('item-path') )
        })

        $(this).find('a[data-item-view]').unbind('click').bind('click', function(event) { 
            $(this).closest('.isocontainer').nextAll().remove()
            var path = $(this).closest('.item').data('item-path')
            var view = $(this).data('item-view') 
            showResourceView( path, view )
        })




    },

});


/////// tools

function json2html(data) {
    var html = '';

    if (Array.isArray(data)) {
        html += '<table>';
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
        html += '<table>';
        for (i in data) {
            var value = data[i];
            if (value) {
                html += '<tr>';
                html += '<th>'+i+'</th>';
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







