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
        console.log(this.data)
        
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
            this.code = $(this).text()
            this.label = 'go'
            this.data = {
                'label': this.label,
                'code': this.code
            }
            this.template = '<button>{{label}}</button><code data-id="'+this.id+'" style="display: none">{{code}}</code>'
            var html = $(this.template).render(this.data)
            $(this).html(html)
        }
        
        $(this).click(function(e) {
            e.preventDefault(); 
            e.stopPropagation();
            var code = $("code[data-id='"+self.id+"']").text()
            //alert(code)
            var h = Function(code);
            h()   
            return false;
        })
    }
}) 


window.customElements.define('xio-code', class extends XIOElement {

    render() {
        var code = $(this).text()
        var h = Function(code);
        //$(this.html() = 
        var element = this.nx.parent()
        h.call(element)   
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
