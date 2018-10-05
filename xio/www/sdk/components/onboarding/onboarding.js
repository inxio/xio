(function() {

var template = `
    <template>

        <div class="card" style="background: none;">
            <form >
                {{#layout.class.full}}
                <div class="card-header">
                    <h3 class="card-title">
                    <img src="sdk/images/icon.png" height="36" class="d-inline-block align-top" alt="" >
                    {{app.about.name}}
                    </h3>
                    
                </div>
                {{/layout.class.full}}

                <div class="card-block" >
                    <div class="form-group">
                        <label for="{{name}}" >Seed</label> 
                        <input type="text" class="form-control" name="seed" required placeholder="Put some seed here ..." />
                        <small id="emailHelp" class="form-text text-muted">Your private key will be generated from your seed.</small>
                    </div>
                    <div >
                    
                        <label data-toggle="collapse" data-target="#collapsePassword">
                            <input type="checkbox"/> Encrypt my private key
                        </label>
                        <div class="form-group collapse" id="collapsePassword" >
                            <input type="text" class="form-control" name="password" placeholder="Password ..." />
                            <small id="emailHelp" class="form-text text-muted">This password will be required for unlock your key.</small>
                        </div>
                    </div>
                       
                    {{^layout.class.full}}
                       <div>
                        <div style="text-align:right">
                            <button type="submit" class="btn btn-primary" >CONNECT</button> 
                        </div>
                        </div>

                    {{/layout.class.full}}

                </div>
                {{#layout.class.full}}
                <div class="card-footer">
                    <div style="text-align:right">
                        <button type="submit" class="btn btn-primary" >CONNECT</button> 
                    </div>
                </div>
                {{/layout.class.full}}
            </form>
        </div>
    </template>
`

window.customElements.define('xio-onboarding', class extends HTMLElement {
    constructor() {
        super();
    }
    connectedCallback() {

        var self = this
        var html = $(template).render({
            'app':app,
            'layout': {
                'class': {
                    'small': true,
                }
            }
        })
        $(this).html( html )
        $(this).find('form').submit(function(e) {
            e.preventDefault();
            try {
                self.submit()
            } catch(error) {
                console.log(error);
            }
            return false;
        })
        $(this).find('a').click(function() {
            $('.signin, .signup').toggle()
        })
    }

    submit() {
        var form = $(this).find('form');
        var seed = form.find("input[name='seed']").val();
        var password = form.find("input[name='password']").val();
        return app.login(seed,password)
    }

    importKey() {
        // https://www.html5rocks.com/en/tutorials/file/dndfiles/  
        var input = document.createElement('input');
        input.type = 'file';
        input.onchange = function(e) {
            var files = e.target.files;
            var file = files[0]
            var reader = new FileReader();
            reader.readAsText(file);
            reader.onload=function(){
                return app.dapp.user.importKey(file.name,reader.result)
            }
        }
        input.click();
    }
   
})


})();
