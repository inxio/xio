

  <script type="text/javascript">
    app.ready(function () {

      f7 = new AppFramework(app)
      f7.init()
      f7.mainView.loadPage('#apps')
    })
  </script>



    <div class="statusbar-overlay"></div>

    <div class="panel-overlay"></div>



    <div class="panel panel-right panel-cover">
      <div class="content-block">
        <div class="content-block-title">Endpoint</div>
        <div class="list-block">
          <ul>

            <li>
                <label class="label-radio item-content">
                <input type="radio" name="endpoint" value="https://api.inxio.net" checked="checked">
                <div class="item-media">
                  <i class="icon icon-form-radio"></i>
                </div>
                <div class="item-inner">
                  <div class="item-title">https://api.inxio.net</div>
                </div>
                </label>
            </li>

            <li>
                <label class="label-radio item-content">
                <input type="radio" name="endpoint" value="http://127.0.0.1:8080">
                <div class="item-media">
                  <i class="icon icon-form-radio"></i>
                </div>
                <div class="item-inner">
                  <div class="item-title">http://127.0.0.1:8080</div>
                </div>
                </label>
            </li>

          </ul>
        </div> 

      </div>
    </div>

    <div class="views">

      <div class="view view-main">

            <div class="navbar">
                <div class="navbar-inner">
                    <div class="center sliding">
                      <img src="sdk/images/icon.png" height="36" class="d-inline-block align-top" alt=""> xio
                    </div>
                    <div class="right"><span id="user-info"></span>
                      <a href="#"  class="link icon-only open-panel" data-panel="right"><i class="icon fa fa-gear"></i></a>
                    </div>

                </div>
                   
            </div>


            <div class="pages navbar-through toolbar-through">

                <div data-page="apps" class="page cached">
                    <div id="apps-content" class="page-content " >
                        APPS
                    </div>
                </div>

                <div data-page="peers" class="page cached">
                     <a href="#index" class="back"> Go back to home page </a>
                    <div id="peers-content" class="page-content " >
                        PEERS
                    </div>
                </div>  
                <div data-page="nodes" class="page cached">
                     <a href="#index" class="back"> Go back to home page </a>
                    <div id="peers-content" class="page-content " >
                        NODES
                    </div>
                </div>  

                <div data-page="cdn" class="page cached">
                    <div class="page-content " >
                        CDN
                    </div>
                </div>  

                <div data-page="app" class="page cached">
                     <div class="toolbar">
                        <div class="toolbar-inner">
                            <div class="left">
                              <a href="#" class="back link">
                                <i class="icon icon-back"></i>
                                <span class="ihm-title">Back</span>
                               </a>
                            </div>
                            <a href="#tab-home"  class="tab-link button active">HOME</a>
                            <a href="#tab-about"  class="tab-link button">ABOUT</a>
                            <a href="#tab-api"  class="tab-link button">API</a>
                            <a href="#tab-tests"  class="tab-link button">TESTS</a>
                            <a href="#tab-stats"  class="tab-link button">STATS</a>

                        </div>
                    </div>

                    <div class="page-content " >

                        <div class="tabs">
                            <div id="tab-home" class="tab active" >
                                    home
                            </div>

                            <div id="tab-about" class="tab" >
                                    about
                            </div>
                            <div id="tab-api" class="tab" >
                               api
                            </div>
                            <div id="tab-tests" class="tab" >
                               tests
                            </div>
                            <div id="tab-stats" class="tab" >
                                stats
                            </div>

                        </div>  
                    </div>
                </div>  

                <div data-page="peer" class="page cached">
                     <div class="toolbar">
                        <div class="toolbar-inner">
                            <div class="left">
                              <a href="#" class="back link">
                                <i class="icon icon-back"></i>
                                <span>Back</span>
                               </a>
                            </div>
                            <div class="center sliding ihm-title">aaa</div>
                            <a href="#tab-about"  class="tab-link button active">ABOUT</a>
                            <a href="#tab-children"  class="tab-link button">WEBSITE</a>
                            <a href="#tab-tests"  class="tab-link button">NEWS</a>

                        <div class="searchbar-input">
                          <input type="search" placeholder="Search"><a href="#" class="searchbar-clear"></a>
                        </div>

                        </div>
                    </div>

                    <div class="page-content " >
                        APP
                    </div>
                </div>  
            </div>


            <div class="toolbar toolbar-bottom">
                <div class="toolbar-inner">
                    <a href="#apps" class="link" >APPS</a>
                    <a href="#peers" class="link" >PEERS</a>
                    <a href="#nodes" class="link" >NODES</a>
                </div>
            </div>



      </div>
    </div>



<!--
<header >
  <nav id="header" class="navbar navbar-toggleable-md fixed-top">
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#containerNavbarCenter" aria-controls="containerNavbarCenter" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
  </button>



    <div class="collapse navbar-collapse " id="containerNavbarCenter">

      <a class="navbar-brand" link="/">
          <img src="sdk/images/icon.png" height="36" class="d-inline-block align-top" alt="" > {{app.about.name}}
      </a>

      <ul class="nav nav-pills mr-auto ">
          <li class="nav-item" ng-repeat="page in app.nav.header" ><a class="nav-link" link="{{page.path}}" data-toggle="pill">{{page.label}}</a> </li> 
      </ul>
              
      <ul class="nav float-xs-right">

         
          <li class="nav-item" ng-if="!app.user.id"><a class="nav-link" link="/inxio/login" >Login</a></li> 

          <li class="nav-item dropdown" ng-if="app.user.id">
            <a class="nav-link dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">{{app.user.name}}</a>
            <div class="dropdown-menu" >
                <a ng-repeat="item in app.user.nav" class="dropdown-item" href="#{{item.path}}">{{item.title}}</a>
                <a class="dropdown-item" link="/inxio/user/dashboard" >Dashboard</a> 
                <a class="dropdown-item" link="/inxio/user/settings" >Settings</a> 
                <a class="dropdown-item" link="/inxio/user/billing" >Billing</a> 
                <a class="dropdown-item" link="/" ng-click="app.user.logout()">Logout</a>
            </div>
          </li>

      </ul>
      

    </div>
  </nav>
</header>

<searchbar ng-if="app.about.searchbar"></searchbar>

<breadcrumb ng-if="app.about.breadcrumb"></breadcrumb>

<ng-transclude></ng-transclude>




<page path="/inxio/login" src="sdk/templates/login.tpl">
</page>

<page path="/inxio/admin" src="sdk/templates/admin.tpl">
</page>


<page path="/inxio/contact" src="sdk/templates/contact.tpl">
</page>

<page path="/inxio/cgu" src="sdk/templates/cgu.tpl">
</page>



<footer>
    <nav id="footer" class="navbar navbar-toggleable-md  fixed-bottom">
      <button class="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse container">

        <div style="display: inline-block;vertical-align: middle; text-align: center;" ng-if="app.status.loading">
          <i class="fa fa-refresh fa-spin"  style="vertical-align: middle; opacity: 0.5">
          </i> LOADING ...
        </div> 

        <span ng-if="!app.about.footer.mention" class="navbar-text mr-auto">
          {{app.about.name}} - v{{app.about.version}}   
        </span>
        <span ng-if="app.about.footer.mention" class="navbar-text mr-auto">
          {{app.about.footer.mention}}   
        </span>
        <span ng-if="app.ext.ethereum.account" class="navbar-text mr-auto">
          Ethereum account {{app.ext.ethereum.account}}
        </span>
        
       
        </ul>
        <ul ng-if="!app.nav.footer" class="nav nav-pills float-xs-right">
            <li class="nav-item"><a class="nav-link" link="/inxio/admin" data-toggle="pill">Admin</a> </li> 
            <li class="nav-item"><a class="nav-link" link="/inxio/contact" data-toggle="pill">Contact</a></li>
            <li class="nav-item"><a class="nav-link" link="/inxio/cgu" data-toggle="pill">GGU</a></li>
        </ul>
        <ul ng-if="app.nav.footer" class="nav nav-pills float-xs-right">
            <li class="nav-item"><a class="nav-link" link="/inxio/admin" data-toggle="pill">Admin</a> </li>
            <li class="nav-item" ng-repeat="page in app.nav.footer" ><a class="nav-link" link="{{page.path}}" data-toggle="pill">{{page.label}}</a> </li> 

        </ul>
      </div>
    </nav>
</footer>
-->
