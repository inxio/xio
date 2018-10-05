(function() {


    var resource_template_response = `
        <div class="card">
            <div class="card-header">
                <h6 class="card-header endpoint">
                {{#error}}HTTP {{status}}
                {{/error}}
                {{^error}}HTTP {{status}}{{/error}}</strong>
                
                <small>{{reason}}</small>

                {{#ihm.content_type}}<span class="label label-default">{{ihm.content_type}}</span>{{/ihm.content_type}}
                <!--
                <a href="#" onclick="openOperationInPopup()" class="btn btn-sm btn-default" style="color: #FFF"><i class="fa fa-link "> </i>mshow headers</a>
                -->
                {{#ihm.fromcache}}
                    <span class="label label-warning" onclick="withoutCache()" > <i class="fa fa-refresh "> </i> from cache</span>
                {{/ihm.fromcache}}

                </h6>
                <div id="subheader" class="subheader" >

                    <ul>
                    {{#headers}}
                        <li>{{name}} : {{value}}</li>
                    {{/headers}}
                    </ul>


                </div>
            </div>

            <div class="card-block">

                <pre><code>{{content}}</code></pre> 

            </div>
        
        </div>
    `


    var resource_template_request = `
            <form data-xio-request-method="{{method}}">
                <div class="card">
                    <div class="card-header">
                        <stong>{{method}}</strong> {{path}}
                    </div>

                    <div class="card-block">
                            {{#input.description}}

                               <p>{{input.description}}</p>
                                {{{input.html}}}
                                <hr/>

                            {{/input.description}}

                            {{#ihm:urlinput}}
                            
                                <xio-input name="{{name}}" type="{{name}}" required="{{required}}"  placeholder="{{description}}">
                                </xio-input>

                            {{/ihm:urlinput}}

                            {{#input}} 
                            
                                {{#body}} 
                                  <input type="text" class="form-control form-control-sm" name="__body__" placeholder="put data here" value="{{value}}"/>
                                {{/body}} 
                                
                                {{#params}} 

                                <xio-input name="{{name}}" type="{{type}}" required="{{required}}" readonly="{{readonly}}" placeholder="{{description}}" value="{{value}}">
                                    {{#options}} 
                                        <option value="{{value}}">{{name}}</option>
                                    {{/options}} 
                                </xio-input>
                                
                                {{/params}} 
                            {{/input}} 
                            
                       
                    </div>
                    <div class="card-footer">
                        <button type="submit" class="btn btn-sm btn-primary" value="" >SUBMIT</button> 
                    </div>
                </div>
                <div class="response"></div>
            </form>
       
    `
    var resource_template = `<div style="border: solid 1px #000">

        <h3>{{about.name}} <small>{{about.id}}</small></h3>


        <nav class="nav nav-tabs">
            <a class="nav-item nav-link active" href="#TAB" data-toggle="tab">HOME</a>
            {{#tabs}}
                <a class="nav-item nav-link" href="#TAB{{method}}" data-toggle="tab">{{method}}</a>
            {{/tabs}}
        </nav>
        <div class="tab-content">
            <div class="tab-pane active" id="TAB">
                <ul>
                    {{#children}}
                        <li><a href="#home?path={{path}}">{{name}}</a></li>
                    {{/children}}
                </ul>
            </div>
            {{#tabs}}
                <div class="tab-pane" id="TAB{{method}}">
                    `+resource_template_request+`
                </div>
            {{/tabs}}
        </div>
    </div>
    `

    app.ext.resource = {
        'requirements': [
            'ext.html',
            'ext.css'
        ]
    }

   
    window.customElements.define('xio-resource', class extends XIOElement {

        constructor() {
            super();
            this.template = resource_template
            this.debug = true
            this.server = app.server
            this.basepath = '/xio/admin/root' //'xio/ext/admin/root'
            this.about = {}
        }

        request(method,path,payload) {
            if (path)
                var fullpath = this.basepath+'/'+path
            else 
                var fullpath = this.basepath
            return this.server.request(method,fullpath,payload)
        }

        render(req) {
            console.log('###### resource render ',req)
            var self = this
            this.path = req['path'] || ''


            return this.request('ABOUT',this.path).then( function(resp) {
                console.log('################ getAbout ',resp.content)
                var about = xio.tools.about(resp.content)
                var template = $(resource_template)
                var data = {
                    'about': about,
                }

                // set options/methods
                var options = ['ABOUT','API','TEST'].concat(about.options)
                var tabs = []
                $(options).each( function(k,v) {
                    var method = v
                    var config = about.methods[v] || {}
                    config['method'] = method
                    tabs.push(config)
                })
                data.tabs = tabs

                // children
                var children = []
                if (about['resources']) {
                    for (var childname in about['resources']) {
                        children.push({
                            'name': childname,
                            'path': self.path+'/'+childname
                        })
                    }
                }
                data.children = children

                var html = template.render(data)
                $(self).html(html)

                $(self).find('form').submit(function(e) {
                    e.preventDefault();
                    try {
                        var form = $(this);
                        var method = form.data('xio-request-method')
                        var payload = { };
                        $.each( form.serializeArray(), function() {
                            payload[this.name] = this.value;
                        }); 
                        self.request(method,self.path,payload).then( function(resp) {

                            if (resp.headers) {
                                //fix des headers
                                resp['ihm'] = {}
                                resp['ihm']['fromcache'] = resp['headers']['xio_cache_ttl']
                                resp['ihm']['content_type'] = resp['headers']['Content-Type']
                                var headers = []
                                for (var k in resp['headers']) {
                                    headers.push({'name': k, 'value': resp['headers'][k]})    
                                }
                                resp['headers'] = headers
                            }

                            if (typeof resp['content'] != 'string')
                                resp['content'] = JSON.stringify(resp['content'] , undefined, 4);

                            //alert( JSON.stringify(resp))
                            var template = $(resource_template_response);
                            var html = $(template).render(resp)
                            $(form).find('.response').html(html)
                        })
                    } catch(error) {
                        console.log(error);
                    }
                    return false;
                })
            })
        }





        
    })

})();


