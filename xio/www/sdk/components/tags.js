(function() {





window.customElements.define('xio-breadcrumb', class extends XIOElement {

    render(data) {
        var self = this
        this.basehref = $(this).attr('basehref') || app.nav.hashbang
        this.path = $(this).attr('path') //|| data.path
        this.handler = $(this).attr('handler')
        if (this.handler)
            this.basehref = ''
        if (this.path) {
            
            var breadcrumb = []
            var p = []
            var parts = this.path.split('/')
            for (var i in parts) {
                var part = parts[i]
                if (part) {
                    p.push(part)
                    breadcrumb.push({
                        'name': part,
                        'href': this.basehref+p.join('/')
                    }) 
                }
            }
            
        } else {
            var breadcrumb = []
            var p = []
            for (var i in data) {
                var part = data[i].name
                if (part) {
                    p.push(part)
                    breadcrumb.push({
                        'name': part,
                        'href': this.basehref+p.join('/')
                    }) 
                }

            }
        }

        this.data = {
            'breadcrumb': breadcrumb,
            'handler': this.handler
        }
        
        
        this.template = `<nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            {{#breadcrumb}}
                <li class="breadcrumb-item"><a href="{{href}}">{{name}}</a></li>
            {{/breadcrumb}}
          </ol>
        </nav>`
        var html = $(this.template).render(this.data)
        $(this).html(html)

        if (this.handler) {

            $(this).find('a').click(function(e) {
                e.preventDefault()
                console.log(this.handler)
                window[self.handler]( $(this).attr('href') )
            })

        }
    }
    



})


window.customElements.define('xio-button', class extends XIOElement {

    render() {
        
        var self = this
        if (!this.id) {
            this.id = app.uuid()
            this.action = $(this).attr('action') || $(this).find('code').text()
            this.code = this.action
            this.label = $(this).attr('label')
            this.type = $(this).attr('type')
            this.value = $(this).attr('value')
            if (!this.type)
                this.type = 'button'
            this.icon = $(this).attr('icon')
            this.options = []
            $(this).find('option').each( function() {
                self.options.push({
                    'label': this.text,
                    'value': this.getAttribute('value'),
                })
            })



            if (!this.icon && !this.label) {
                this.label = 'ok'
            }

            console.log(this.data)
            
            if(!$(this).hasClass('btn')) {
                $(this).addClass('btn btn-sm btn-primary')
            } 
            this.class = $(this).attr('class')
            $(this).removeClass();

            this.data = {
                'label': this.label,
                'icon': this.icon,
                'code': this.code,
                'options': this.options,
                'type': this.type
            }

            this.template = `<div>
                {{^options.length}}
                    <button class="`+this.class+`" type="{{type}}" data-action="auto">
                        <i class="fa fa-{{icon}}"> </i> {{label}}
                    </button>
                {{/options.length}}
                
                {{#options.length}}
                    <div class="dropdown">
                        <button class="`+this.class+` dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" id="dropdownMenu2">
                            <i class="fa fa-{{icon}}"> </i> {{label}}
                        </button>
                        <div class="dropdown-menu" aria-labelledby="dropdownMenu2">
                            {{#options}}
                                <button class="dropdown-item" type="button" data-action="auto" data-value="{{value}}">{{label}}</button>
                            {{/options}}
                        </div>
                    </div>

                {{/options.length}}
                <code data-id="`+this.id+`" style="display: none">{{code}}</code>
                </div>
            `
            var html = $(this.template).render(this.data)
            $(this).html(html)
        }

        if (this.type!='submit') {
            $(this).find('button[data-action]').click(function(e) {
                //e.preventDefault(); 
                //e.stopPropagation();
                var action = $(this).data('action')
                var value = $(this).data('value')
                this.value = value
                if (action=='auto') {
                    var code = $("code[data-id='"+self.id+"']").text()
                    //alert(code)
                    var h = Function(code);
                    h.apply(this)   
                } else {
                    // ??
                }

                //return false;
            })
        }

  


    }
}) 


window.customElements.define('xio-sample', class extends XIOElement {



    getTemplate() {
        
        return `<fieldset style="border: solid 1px #ccc !important;">
                <legend>{{label}}</legend>
                <div class="row">
                    <div class="col-6 bg-light text-dark">
                        <pre><code>{{code}}</code></pre>
                    </div>
                    <div class="col-6 slot">
                       
                    </div>

                </div>
            </fieldset>
        `
    }

    init() {
        var self = this
        this.nx.data = {
            'label': $(this).attr('label') || 'sample',
            'code': $(this).html()
        }

    }
}) 



window.customElements.define('xio-card', class extends XIOElement {
    
    connectedCallback() {
        var self = this

        var template = `<div class="card bg-info">
                <div class="card-body">
                    <h5 class="card-category card-category-social">
                        <i class="fa fa-user"></i> User
                    </h5>
                    <h4 class="card-title">
                        <a href="#pablo">{{title}}</a>
                    </h4>
                    <div class="slot">
                    </div>
                </div>
                <div class="card-footer">
                    <div class="author">
                        {{#icon}}<img src="{{icon}}" alt="..." class="avatar img-raised">{{/icon}}
                        {{#url}}<span>{{url}}</span>{{/url}}
                       
                    </div>
                    <!--
                    <div class="stats ml-auto">
                        <i class="material-icons">apps</i> 45
                    </div>
                    -->
                </div>
            </div>
        `

        var data = {
            type: $(this).attr('type'),
            title: $(this).attr('title'),
            description: $(this).attr('description'),
            icon: $(this).attr('icon'),
            url: $(this).attr('url'),
        }

        
        if (!$(this).hasClass('wrapped')) {
            $(this).addClass('wrapped')
            window.setTimeout(function() {

                var content = self.innerHTML

                var html = $(template)
                html.render(data)
                html.find('.slot').html( content )

                $(self).html(html)

            }, 0);
        }

    }
    
})






})();
