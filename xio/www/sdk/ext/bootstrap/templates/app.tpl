
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
          <li class="nav-item" ng-repeat="page in app.about.sitemap" ><a class="nav-link" link="{{page.path}}" data-toggle="pill">{{page.label}}</a> </li> 
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
