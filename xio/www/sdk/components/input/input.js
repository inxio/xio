
(function() {

    var template = `
        {{#type_hidden}}
            <input type="hidden" class="form-control form-control-sm" name="{{name}}" value="{{value}}" />
        {{/type_hidden}}
        {{^type_hidden}}
        <div class="form-group row">
            <label for="{{name}}" class="col-sm-2 col-form-label">{{name}} {{#required}}<span class="badge badge-pill badge-danger">Required</span>{{/required}}</label> 
            <div class="col-sm-10">
                
                    {{#type_textarea}}
                        <textarea class="form-control form-control-sm" name="{{name}}" placeholder="{{description}}">{{value}}</textarea>
                    {{/type_textarea}}
                    {{#type_script}}
                        <textarea class="form-control form-control-sm" rows="10" name="{{name}}" placeholder="{{description}}">{{value}}</textarea>
                    {{/type_script}}
                    {{#type_password}}
                        <input type="password" class="form-control form-control-sm" name="{{name}}" placeholder="{{description}}" value="{{value}}" />
                    {{/type_password}}   
                    {{#type_text}}
                        <input type="text" class="form-control form-control-sm" name="{{name}}" placeholder="{{description}}" value="{{value}}" {{readonly}}/>
                    {{/type_text}}
                    {{#type_mail}}
                        <input type="mail" class="form-control form-control-sm" name="{{name}}" placeholder="{{description}}" value="{{value}}" />
                    {{/type_mail}}
                    {{#type_url}}
                        <input type="text" class="form-control form-control-sm" name="{{name}}" placeholder="{{description}}" value="{{value}}" />
                    {{/type_url}}
                    {{#type_select}}      
                        <select class="form-control form-control-sm" name="{{name}}">
                            {{#options}} 
                                <option value="{{value}}">{{name}}</option>
                            {{/options}} 
                        </select >
                    {{/type_select}}
            </div>
        </div>
        {{/type_hidden}}
    `
    
    app.tag('xio-input').bind( class extends XIOElement {

        init() {
            this.name = $(this).attr('name')

            var type = $(this).attr('type') || 'text'
            var info = type.split('/')
            this.type = info[0]
            this.subtype = info[1]
            this.value = $(this).attr('value') || $(this).text() 
            this.required = false
            this.readonly = $(this).attr('readonly')=='true'
        }

        getTemplate() {
            return template
        }
        getData() {
            this.required = this.getAttribute('required')
            var options = []
            $(this).find('option').each(function(k,v) {
                options.push({
                    'name': $(this).attr('name') || this.text,
                    'value': $(this).attr('value') || this.text
                })
            })

            var data = {
                'name': this.name,
                'type': this.type,
                'required': this.required,
                'options': options,
                'value': this.value,
            }
            if (this.readonly)
                data.readonly = 'readonly'
            data['type_'+this.type] = true
            console.log(data)
            return data
        }

        
    })



    app.tag('xio-form').bind( class extends XIOElement {

        getTemplate() {
            return `
            <form>
                <header>header
                </header>
                <section class="slot">
                </section>
                <footer>
                    <button type="submit" >go</button>
                    <xio-button type="submit" label="submit"></xio-button>
                </footer>
            </form>
        `
        }

        render() {
            var self = this
            super.render().then(function() {
                $(self).find('form').submit( function(e) {
                    e.preventDefault();
                    try {
                        self.submit()
                    } catch(e) {
                        self.log.error('ERROR',e)
                    }
                    return false;
                })
                
            })
        }

        submit() {
            var form = $(this).find('form');
            var data = { };
            $.each( form.serializeArray(), function() {
                data[this.name] = this.value;
            }); 
            this.emit('submit',data)
        }
        
    })


})();

