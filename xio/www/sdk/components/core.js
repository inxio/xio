

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
    }

    connectedCallback() {
        var self = this
        console.log('connectedCallback =====================================',this.nodeName,this.id)
        this.nx.parent = $(this).parent().closest('.xio-element')[0]
        //console.log('connectedCallback PARENT =====================================',this.nx.parent)
        if (this.nx.parent)
            this.nx.parent.nx.children.push(this)

        $(this).addClass('xio-element')

        this.debug = $(this).hasClass('debug')

        if (this.nx.RENDER_ON_CLOSE) {
            
        } else {
            window.setTimeout(function() {
                self._render()
            })
        }

    }

    on(topic,callback) {
        if (!this.nx.events[topic])
            this.nx.events[topic] = []
        this.nx.events[topic].push(callback)
    }

    emit(topic,data) {
        var self = this
        console.log('pub',topic)
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

    _load() {
        var self = this

        if (this.debug)
            console.log('LOAD =====================================',this)

        var d1 = self.getData()
        var d2 = self.getTemplate()
        var d3 = self.getContent()

        return $.when(d1,d2,d3).done(function(data,template,content) {

            //if (self.debug)
            console.log('LOADED =====================================',self.nodeName,self.id,data,template,content)

            self.nx.data = data
            self.nx.template = template
            self.nx.content = content
        })
    }

    getContent() {
        var self = this
        var result = null
        var src = $(this).attr('include')
        if (src) {
            return app.load(src).then(function(content) { 
                // handle json (cf cio-include)
                if (content instanceof Object)
                    content = $.trim( JSON.stringify(content) )

                return content
            })
        } else {
            return self.innerHTML
        }
    }

    getTemplate() {
        if (this.template)
            return this.template
        var self = this
        var src = $(this).attr('template')
        if (src) {
            return app.load(src).then(function(content) { 
                return content
            })
        }
    }

    getData() {
        if (this.data)
            return this.data

        var self = this
        var data = null

        return data
    }

    _render(data) {
        var self = this

        if (this.nx.rendered) {
            var d =  $.Deferred(); 
            d.resolve(this.nx.rendered)
            return d.promise()
        }

        this.nx.rendered = true
        //alert('RENDER '+self.nodeName+' ID '+self.id)

        if (this.ctrl && this.ctrl.render) {
            console.log('RENDER DELEGATE>>',this.ctrl)
            return this.ctrl.render(data)
        }

        console.log('#RESOURCE RENDER >>',this.nodeName,this.id,data)

        if (self.debug)
            console.log('RENDER =====================================',this.nodeName,this.id, this.nx.template)

        return this._load().then(function() {

            console.log(self.nodeName,self.nx)
            
            var content = self.nx.content
            var template = self.nx.template

            // init data
            var data = self.nx.data || {}
            data['app'] = app


            // init template
            if (template) {
                var $template = $('<div>'+template+'</div>') // pb avec find .slot si tag template
                $template.find('.slot').html(content)
            } else {
                var $template = $('<template>'+content+'</template>')
            }
            var html = $template.render(data)

            if (self.debug) {
                console.log('RENDER CONTENT =====================================',content)
                console.log('RENDER TEMPLATE =====================================',$template[0].outerHTML)
                console.log('RENDER DATA =====================================',data)
                console.log('RENDER RENDERED =====================================',html)
            }

            
            self.nx.rendered = html

            // set flag active for auto render of children
            $(self).addClass('active')

            // update node
            $(self).html(html)
            
            // render child
            //alert('RENDER CHILD OF '+self.nodeName+' ID '+self.id)
            /*
            $(self).find('.xio-element').each(function() {
                this.render(data)
            })
            */
            
            
        }).then(function() {
            self.nx.status = 9
            if (self.nx.parent)
                self.nx.parent._refresh()
        })
    }


    
}



window.customElements.define('xio-page', class extends XIOElement {

    getTemplate() {
            return `<div class="page slot">
                       page
                    </div>
        `
    } 
    nooconnectedCallback() {
      // prevent auto rendering + hide by default
      $(this).hide()
    }

    render(data) {
        var self = this
        var d = super.render(data).then(function() {
            
            $('xio-page').hide()
            $(self).show()
        })

        return d
    }


})



window.customElements.define('xio-section', class extends XIOElement {

    getTemplate() {
        return `<section class="slot"></section>`
    } 
    


})


window.customElements.define('xio-data', class extends XIOElement {

    constructor() {
        super();   
        this.nx.RENDER_ON_CLOSE = true
    }


    render() {
        var self = this
        self.data = null
        self.raw = $.trim( self.textContent )
        self.name = $(self).attr('name')
        try {
            self.data = JSON.parse( self.raw )
        } catch(e) {
            $(self).attr('error',e)
        }
        
        //var el = self.nx.getParent()
        //el.nx.data = {}
        //el.nx.data[self.name] = self.data

        //alert(el.nx.data[this.name])

    }
    /*
    render() {
        
        var self = this
        super.render().then( function() {
            self.data = null
            self.raw = self.nx.content
            self.name = $(self).attr('name')
            try {
                self.data = JSON.parse( self.raw )
            } catch(e) {
                
                $(self).attr('error',e)
            }
            
            var el = self.nx.getParent()
            if (el && el.nx) {
                el.nx.data = {}
                el.nx.data[self.name] = self.data
            }
        })
    }
    */
    
})




window.customElements.define('xio-include', class extends XIOElement {

    render() {
        var self = this
        this.src = $(this).attr('src')
        if (this.src) {
            //app.log.info('including '+this.src)
            console.log('including '+this.src)
            return app.load(this.src).then( function(content) {
                if (content instanceof Object)
                    content = $.trim( JSON.stringify(content) )
                $(self).replaceWith(content)
            })
        }

    }
    
})


