

class XIOElement extends HTMLElement {
    
    constructor() {
        super();   
        var self = this
        this.nx = {}    
        this.nx.children = []
        this.nx.events = {}
        this.nx.getParent = function() {
            console.log($(self).closest('body').html())
            return $(self).parent().closest('.xio-element')[0]
        }
        this.debug = $(this).hasClass('debug')
    }

    connectedCallback() {
        var self = this
        if (app._ready) {
            this.log('connectedCallback')
            //window.setTimeout(function() {
                self._init().then(function() {
                    return self.render()
                })
            //},0)
        }

    }

    init() {
        // to be overwrited
    }

    _init() {
        var self = this
        this.nx.parent = $(this).parent().closest('.xio-element')[0]
        if (this.nx.parent)
            this.nx.parent.nx.children.push(this)

        if (this.nx.initialized) {
            return
        }
        this.log('init')
        this.nx.initialized = true
        $(this).addClass('xio-element')
        var d = this.init()
        return $.when( d )
    }


    _load() {
        var self = this
        if (this.nx.loaded)
            return this.nx.loaded
        
        this.log('LOAD')
        
        var d1 = self._getData()
        var d2 = self._getTemplate()
        var d3 = self._getContent()

        this.nx.loaded = $.when(d1,d2,d3).done(function(data,template,content) {
            self.nx.data = data
            self.nx.template = template
            self.nx.content = content
            self.log('LOADED',self.nx)
        })
        return this.nx.loaded
    }


    _getContent() {
        var self = this
        var result = null
        var src = $(this).attr('content')
        if (src) {
            
            return app.load(src).then(function(content) { 

                // handle json (cf cio-include)
                if (content instanceof Object)
                    content = $.trim( JSON.stringify(content) )

                return content
            })
        } else if (self.getContent) {
            return self.getContent()
        } else {
            return self.innerHTML
        }
    }

    _getTemplate() {
        var self = this
        var src = $(this).attr('template')
        if (src) {
            return app.load(src).then(function(template) { 
                return template
            })
        } else if (self.getTemplate) {
            return self.getTemplate()
        }
    }

    _getData() {
        var self = this
        var src = $(this).attr('data')
        if (src) {
            return app.load(src).then(function(data) { 
                return data
            })
        } else if (self.getData) {
            return self.getData()
        }
    }


    render() {
        var self = this
        return this._load().then( function() {

            if (self.nx.rendered)
                return 

            self.log('RENDER')
            
            var content = self.nx.content
            var template = self.nx.template
            var data = self.nx.data || {}
            data['app'] = app

            if (template) {
                var $template = $('<div>'+template+'</div>') // pb avec find .slot si tag template
                $template.find('.slot').html(content)
            } else {
                var $template = $('<template>'+content+'</template>')
            }
            var html = $template.render(data)
            self.nx.rendered = html
            $(self).html(html)
            self.emit('rendered')
        })
    }



    log(msg) {
        var args = $.makeArray(arguments)
        args.unshift('===================================== #'+this.nodeName)
        if (this.nx.debug)
            console.log.apply(this,args)
    }


    on(topic,callback) {
        if (!this.nx.events[topic])
            this.nx.events[topic] = []
        this.nx.events[topic].push(callback)
    }

    emit(topic,data) {
        var self = this
        self.log('publish',topic)
        if (this.nx.events[topic])
            $(this.nx.events[topic]).each(function(){
                this(self,data)
            })
    }

    _refresh() {

        //alert( this.nodeName+' refresh')
        var counter = 0
        for (var i in this.nx.children) {
            var child = this.nx.children[i]
            if (child.nx.status!=9) {
                return 
            }
        }
        //alert(this.nodeName+' ready '+i)
        this.render()
    }




    
}




window.customElements.define('xio-app', class extends XIOElement {

    getTemplate() {
        return `<header id="xio-app-header">
            <nav id="xio-app-nav" class="navbar navbar-toggleable-md fixed-top">
                <div class="container ">
                    <a class="navbar-brand" href="#">
                        <img src="sdk/images/icon.png" height="36" class="d-inline-block align-top" alt="" > {{app.about.name}} 
                    </a>

                    <ul class="nav nav-pills mr-auto ">
                      {{#app.layout.slot.header.links}}
                        <li class="nav-item"><a class="nav-link" href="{{path}}" >{{label}}</a> </li> 
                      {{/app.layout.slot.header.links}}
                    </ul>
                          
                    <ul class="nav float-xs-right">

                        {{#app.user.id}}
                        
                            {{#app.about.search}}
                                <xio-search></xio-search>
                            {{/app.about.search}}
                        
                          <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" data-toggle="dropdown" data-nx-binded="app.user.id">{{app.user.id}}</a>
                            <div class="dropdown-menu" >
                              {{#app.layout.slot.user.links}}
                                <a class="dropdown-item" href="{{path}}">{{label}}</a>
                              {{/app.layout.slot.user.links}}
                              <div class="dropdown-divider"></div>
                              <a class="dropdown-item" href="javascript:app.logout()">LOGOUT</a>
                            </div>
                          </li>
                        {{/app.user.id}}
                        {{^app.user.id}}
                          {{#app.about.user.link}}
                          <li class="nav-item"><a class="nav-link btn btn-primary btn-sm" href="{{app.about.user.link}}" >CONNECT</a> </li> 
                          {{/app.about.user.link}}
                        {{/app.user.id}}
                    </ul>
                </div>

            </nav>

            {{#app.user.id}}
            <nav id="xio-app-toolbar" class="navbar navbar-toggleable-md fixed-top" >
                <div class="container ">
                    
                    <ul class="nav nav-pills mr-auto ">
                      {{#app.layout.slot.toolbar.links}}
                        <li class="nav-item"><a class="nav-link" href="{{path}}" >{{label}}</a> </li> 
                      {{/app.layout.slot.toolbar.links}}
                    </ul>
                          
                    <ul class="nav float-xs-right">
                      {{#app.layout.slot.toolbar.button}}
                        <li class="nav-item"><a class="nav-link" href="{{path}}" >{{label}}</a> </li> 
                      {{/app.layout.slot.toolbar.button}}
                    </ul>
                    <xio-search class="xio-dev"></xio-search>
                </div>
            </nav>

            {{/app.user.id}}

        </header>



        <div style="padding-top: 100px; padding-bottom: 100px;" class="container">  

            <div class="container ">
                <xio-breadcrumb>aa</xio-breadcrumb>
            </div>

            <xio-page id="login">
                landing
                <xio-onboarding>
                </xio-onboarding>
            </xio-page>

            <div class="slot">
            </div>



        </div>


        <footer id="xio-app-footer">
            <nav  class="navbar navbar-toggleable-md  fixed-bottom">


                <div class="container">

                    <div style="display: inline-block;vertical-align: middle; text-align: center; display: none" data-xio-if="app.status.loading">
                      <i class="fa fa-refresh fa-spin"  style="vertical-align: middle; opacity: 0.5">
                      </i> LOADING ...
                    </div> 

                    <span class="navbar-text mr-auto text-muted">
                     {{{app.about.footer.text}}} 
                    </span>



                    </ul>
                    <ul class="nav nav-pills float-xs-right">
                        {{#app.layout.slot.footer.links}}
                          <li class="nav-item"><a class="nav-link" href="{{path}}">{{label}}</a> </li> 
                        {{/app.layout.slot.footer.links}}
                        
                    </ul>
                </div>
            
            </nav>
        </footer>
        `;
    }
    init() {
        $(this).hide()
    }
    render() {
        var self = this
        return super.render().then( function() {
            $(self).show()
        })
    }
    
})







window.customElements.define('xio-page', class extends XIOElement {

    getTemplate() {
        return `<div class="page slot">
                       page
                    </div>
        `
    } 
    init() {
        // prevent auto rendering + hide by default
        $(this).hide()
    }

    render() {
        var self = this
        return super.render().then( function() {
            $('xio-page').hide()
            $(self).show()
        })
    }

})



window.customElements.define('xio-section', class extends XIOElement {

    getTemplate() {
        return `<section class="slot"></section>`
    } 
    


})


window.customElements.define('xio-data', class extends XIOElement {

    render() {
        var self = this
        return super.render().then( function() {
            self.raw = $.trim( self.nx.content )
            self.name = $(self).attr('name')
            try {
                self.data = JSON.parse( self.raw )
                if (self.nx.parent) {
                    if (self.nx.parent.nx.data==undefined)
                        self.nx.parent.nx.data = {}
                    self.nx.parent.nx.data[self.name] = self.data
                }
            } catch(e) {
                $(self).attr('error',e)
            }
        })
    }
    
})




window.customElements.define('xio-include', class extends XIOElement {

    render() {
        var self = this
        this.src = $(this).attr('src')
        if (this.src) {
            return app.load(this.src).then( function(content) {
                if (content instanceof Object)
                    content = $.trim( JSON.stringify(content) )
                $(self).replaceWith(content)
            })
        }

    }
    
})


