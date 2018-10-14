


window.customElements.define('xio-app', class extends XIOElementApp {

    getTemplate() {
        return `
            <div id="app">

                <!-- Status bar overlay for fullscreen mode-->
                <div class="statusbar"></div>

                <!-- Left panel with cover effect-->
                <div class="panel panel-left panel-cover theme-dark">
                  <div class="view">
                    <div class="page">
                      <div class="navbar">
                        <div class="navbar-inner">
                          <div class="title">Left Panel</div>
                        </div>
                      </div>
                      <div class="page-content">
                        <div class="block">Left panel content goes here</div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Right panel with reveal effect-->
                <div class="panel panel-right panel-reveal theme-dark">
                  <div class="view">
                    <div class="page">
                      <div class="navbar">
                        <div class="navbar-inner">
                          <div class="title">Right Panel</div>
                        </div>
                      </div>
                      <div class="page-content">
                        <div class="block">Right panel content goes here</div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Your main view, should have "view-main" class -->
                <div class="view view-main ios-edges">


                  <!-- Top Navbar -->
                  <div class="navbar">
                    <div class="navbar-inner">
                      <div class="left">
                        <a href="#" class="link icon-only panel-open" data-panel="left">
                          <i class="icon f7-icons ios-only">menu</i>
                          <i class="icon material-icons md-only">menu</i>
                        </a>
                      </div>
                      <div class="title sliding">My App</div>
                      <div class="right">
                        <a href="#" class="link icon-only panel-open" data-panel="right">
                          <i class="icon f7-icons ios-only">menu</i>
                          <i class="icon material-icons md-only">menu</i>
                        </a>
                      </div>
                    </div>
                  </div>

                  <!-- Toolbar-->
                  <div class="toolbar">
                    <div class="toolbar-inner">
                      <a href="/p1/" class="link">page1</a>
                      <a href="/p2/" class="link">page2</a>
                      <a href="/home/" class="link">home</a>
                    </div>
                  </div>
                  <!-- Scrollable page content-->




                    <div class="page" data-name="p1">
                        <div class="page-content">
                            page1
                        </div>
                    </div>

                    <div class="page" data-name="p2">
                        <div class="page-content">
                            page2
                        </div>
                    </div>



                    <xio-page id="home">
                        home
                    </xio-page>

                    <xio-page id="debug">
                        debug
                    </xio-page>

                </div>
            </div>
            `;
    }

    render() {
        var self = this
        return super.render().then( function() {
            window.f7 = self.f7 = new F7()
        })
    }
    
})


window.customElements.define('xio-page', class extends XIOElementPage {


    getTemplate() {
        return `
          <div class="page" data-name="`+this.id+`">

            <div class="page-content slot">


            </div>

          </div>
        </div>

        `;
    }


    render() {
        var self = this
        return super.render().then( function() {
            f7.mainView.router.navigate('/')
        })
    }

    

})





