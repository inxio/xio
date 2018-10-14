

console.log('init bootstrap ')




window.customElements.define('xio-app', class extends XIOElementApp {

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
    
    
})




window.customElements.define('xio-page', class extends XIOElementPage {

    getTemplate() {
        return `<div class="page slot">
                       page
                    </div>
        `
    } 
    

})






