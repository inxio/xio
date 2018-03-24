(function() {

    var doc = document.currentScript.ownerDocument;
    
    //var template = doc.querySelector('template');
    // not work if not inline script ???
    //alert(template)

    var template = `<template>
        <div style="border:solid 1px #000 view="map.function">
            <header>
                <h1>{{endpoint}}</h1>
                <h4>{{about.id}}</h4>
                <h4>{{about.name}}</h4>

                {{#about.options}}
                    <button label="functions">{{.}}</button>
                {{/about.options}}
            </header>
            <div>
                {{#about.resources}}

                {{/about.resources}}

            </div>
        </div>
    </template>
    `;


    /*

    pb implementaion xio.js (inherance resource/app missing)
    */

    ResourceCtrl = function(endpoint) {
        this.app = xio.app(endpoint)
        this.path = ''
        return this
    }
    ResourceCtrl.prototype.about = function(path) {
        path = path || ''

        var d = $.Deferred();
        var self = this
        this.app.request('ABOUT',path,{}, function(resp) {

            var data = resp.content

            data = self.fixAbout(data,path)

            d.resolve(data);
            /*

            if (error) {
                d.reject(error);
            } else {
                d.resolve(result);
            }

            var data = app.fixApi(data,path)
            var html = $('#tpl-api').render(data)
            $('#resource-api').html(html)
            enhance($('#resource-api'))
            */
        })

        return d.promise()

    }
    ResourceCtrl.prototype.fixAbout = function (data,basepath) {
        
        data['ihm:api'] = this.fixApi( data['api']  , basepath)    

        data['ihm:editable'] = (data['@type']=='profile' || data['@type']=='shortcut')

        // fix des options
        data['options'] = ['ABOUT','API','STATS','TEST']
        /*
        var resource_methods = data['api']['/']
        for (method in resource_methods)
            data['options'].push(method)
        */
        return data
    }
    ResourceCtrl.prototype.fixApi = function (api,basepath) {
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


    
    window.customElements.define('xio-resource', class extends HTMLElement {
        constructor() {
            super();
        }
        connectedCallback() {
            var endpoint = $(this).attr('uri')
            this.resource = new ResourceCtrl(endpoint)
            this.render()
        }
        render() {

            var data = {
                'endpoint': this.resource.app._endpoint
            }
            var html = $(template).render(data) 
            $(this).html( html );

            var self = this
            this.resource.about().then( function (data) {

                console.log(data)

                //alert( JSON.stringify(data))
                var data = {
                    'about': data,
                    'endpoint': self.resource.app._endpoint
                }
                var html = $(template).render(data) 

                $(self).html( html );
            })



        }
    })

})();



