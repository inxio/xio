


// links handler

app.nav.links.bind('view',{
    handler: function(view,element,scope) {
      var viewcontainer = element.parents('[view]')
      var viewscope = viewcontainer.scope()
      var values = view.split('.')
      var view = values[0]
      var subview = values[1]
      viewscope.view = view
      viewscope.subview = subview
      viewscope.$parent.$apply();
    }
})




// tags


app.tags.bind('view', {
  restrict: 'A',
  link: function ($scope, $element, $attrs, $ctrl) {
    var values = $attrs.view.split('.')
    var view = values[0]
    var subview = values[1]
    if (view)
      $scope.view = view
    if (subview)
      $scope.subview = subview
  }
});


app.tags.bind('link', {
    restrict: 'A',
    scope: true,
    link: function(scope, element, attrs) {
        element.addClass('inxio-link')
        element.addClass('btn btn-outline-secondary')
        element.click( function(e) {
            var info = attrs.link.split(':')
            if (info.length>1) {
                var ns = info[0]
                var ref = info[1]
                //alert(ns+' '+ref)
                var handler = app.nav.links[ns].handler
                handler(ref,element,scope)
                e.stopPropagation();
                return false;
            } else {
                app.nav.goto(attrs.link)
            } 

        })
    },

});  


app.tags.bind('src', {
    restrict: 'A',
    link: function(scope, element, attrs) {
      var info = attrs.src.split(':')
      var ns = info.shift() 
      var binded = app.nav.links[ns]
      if (binded) {
          var ref = info.join(':')
          var handler = app.nav.links[ns].handler
          console.log(element)
          var value = handler(ref,element,scope)
          element.attr('src',value)
      } 
    },

});  


//app.angular.directive('icon', function($compile) {
app.tags.bind('icon', function($compile) {
    return {
      restrict: 'A',
      scope: true,
      priority: 10,
      link: function(scope, element, attrs) {
        scope.label = attrs.label || element.text()
        scope.icon = attrs.icon
        element.addClass('inxio-link')
        element.html(`<i class="fa fa-{{icon}}"></i> {{label}}`);
        $compile(element.contents())(scope);
      },
    }
})



app.angular.directive('button', function($compile) {
    return {
      restrict: 'E',
      scope: true,
      controller: function ($scope,$element) {
        this.code = $element.text()
      },
      link: function ($scope, $element, $attrs, $ctrl) {
        //alert($element.html())
        var script = $element.find('code')

        if (script.length) {
            $ctrl.code = script.html()
            //alert($ctrl.code)
            $element.html( $attrs.label || 'go')    
            $element.addClass('btn-primary')
            $element.click( function (e) {
              app.log.debug('eval code '+$ctrl.code)  
              var h = Function('scope',$ctrl.code);
              h($scope.$parent)
              $scope.$parent.$apply();
              e.stopPropagation();
              return false;
            })
        }
        if ($attrs.label) {
            $element.html( $attrs.label || 'go')    
            $element.addClass('btn-primary')
        }
         
      },
}})



app.angular.directive('oldbutton', function($compile) {
    return {
  restrict: 'E',
  scope: {
    icon: "@",
    view: "@",
    label: "@",
    action: "@"
  },
  replace:true,
  controller: function ($scope,$element) {
    this.code = $element.text()
  },
  link: function ($scope, $element, $attrs, $ctrl) {
      $element.addClass('btn')
      if ($attrs.action) {
        $ctrl.code = $attrs.action
      }

      if ($attrs.view) {
        var values = $attrs.view.split('.')
        var view = values[0]
        var subview = values[1]
        $element.addClass('btn-outline-secondary')
        $element.click( function (e) {
          var viewcontainer = $element.parents('[view]')
          var viewscope = viewcontainer.scope()
          viewscope.view = view
          viewscope.subview = subview
          viewscope.$parent.$apply();
          e.stopPropagation();
          return false;
        })
      } else if($ctrl.code) {
        $element.addClass('btn-primary')
        $element.click( function (e) {

          var h = Function('scope',$ctrl.code);
          h($scope.$parent)
          $scope.$parent.$apply();
          e.stopPropagation();
          return false;
        })
      } 

      $element.html(`<i ng-if="icon" class="fa {{icon}}"></i> {{label}}`);
      $compile($element.contents())($scope);
  },
}})


app.tags.bind('require', {
  restrict: 'A',
  link: function(scope, element, attrs,ctrl) {

      app.ext.load(attrs.require, function() { 
          scope.$apply();
      })

  },
}); 


app.tags.bind('require', {
    restrict: 'E',
    scope: {
      ext: '@',  
    },
    controller: ['$scope','$element','$q','$rootScope',function ($scope,$element,$q,$rootScope) {   
      this.ext = $scope.ext
      this.load = function() {
          var defer = $q.defer();
          defer.promise.then(function () {
              
              //$rootScope.$apply()
          })
          app.ext.load(this.ext,function() {
              defer.resolve(); 
          })
      }
    }],
    link: function(scope, element, attrs,ctrl) {
      ctrl.load()
    },
}); 



app.angular.directive('data', function($q) {
    return {
      restrict: 'A',
      scope: true,
      link: function(scope, element, attrs) {

          var load = function(src) {
              console.log('... fetching data from '+src)
              var defer = $q.defer();
                  defer.promise.then(function (data) {
                  scope.data = data;
                  console.log(data)
              })
              app.http.get(src).then( function(data) {
                  defer.resolve(data); 
              })
          }
          attrs.$observe('data', function(val){ load(val) });
          load(attrs.data)
      },
  }
})

app.tags.bind('data', {
  restrict: 'E',
  controller: ['$scope','$element','$q',function ($scope,$element,$q) {
    console.log('DATA TAG ============')
    this.name = $element.attr('name')
    this.src = $element.attr('src')
    this.code = $element.text()
    this.load = function(src) {

      console.log('LOADING DATA '+src)
      var defer = $q.defer();
      var self = this
      defer.promise.then(function (data) {
          //alert("loaded "+data)
          if (!$scope.data) {
            $scope.data = {}
          }
          $scope.data[self.name] = data;
          console.log($scope.data)
      });

      if (src) {
        app.http.get(src).then( function(data) {
            defer.resolve(data); 
        })
      } else if (this.code) {
        this.handler = Function('defer',this.code);
        this.handler(defer)
      }
    }

    //this.load()
  }],
  link: function(scope, element, attrs, ctrl) {

    attrs.$observe('src', function(val){ ctrl.load(val) });
    ctrl.load(attrs.src) 
    //element.empty()

  },
});  



app.tags.bind('page', {
  restrict: 'E',
  scope: {
    active: '@',
  },
  transclude: true,
  controller: ['$scope', '$http','$element','$q',function ($scope,$http,$element,$q) {
    this.path = $element.attr('path')
    this.context = app.nav.context
    this.datasource = $element.attr('datasource')
    this.src = $element.attr('src')
    this.active = ($element.attr('active')=='true')
    this.actived = function() {
        return ($element.attr('active')=='true')  
    }

    this.data = {}

    $scope.status = 'loading'
    if (this.datasource) {
      console.log('LOAD DATA', this.datasource)

      var defer = $q.defer();

      app.http.get(this.datasource).then( function(data) {
        console.log('LOADED DATA', data)
        defer.resolve(data);
      })

      defer.promise.then(function (data) {
          $scope.data = data;
          $scope.status = 'loaded'
      });

    }
  }],      
  link: function(scope, element, attrs, ctrl, transclude) {
    ctrl.active = attrs.hasOwnProperty('active') // pb renvoit true ...
    /*
    transclude(scope, function(content) {
        element.find('section').append(content);
    });
    */
  },
  controllerAs: 'page', 
  template: function(elem,attrs,ctrl) {
      if (!attrs.src) {
        return `<div ng-if="page.actived()"><ng-transclude>ng-transclude></div>`  
      } else {
        return `<div ng-if="page.actived()"><ng-include src="'`+attrs.src+`'"></ng-include></div>`
      }
  }
});  



app.angular.directive('section', function($compile) {
  return {
    restrict: 'E',
    link: function(scope, element, attrs, ctrl, transclude) {
      if (!attrs.src) {
        return 
      }
      var tpl = `<ng-include src="'`+attrs.src+`'"></ng-include>`
      var markup = $compile(tpl)(scope);
      //alert(markup)
      element.append(markup);
    },
  }
});  






app.tags.bind('hook', {
  restrict: 'E',
  controller: function ($scope,$element) {
    var code = $element.text()
    this.hook = Function('scope',code);
    $element.empty()
  },
  link: function(scope, element, attrs, ctrl) {
    ctrl.hook(scope)
  },
}); 







app.tags.bind('field', {
  restrict: 'E',
  scope : {
    name : "@",
    type : "@",
    label: "@",
    value: "@",
    required: "@",
    placeholder: "@",
  },
  link: function(scope,element,attrs)
  {
      // bug angular avec attr required ({{required ne passe pas}})
      // ng-attr-required="{{required || undefined}}"  
      scope.noooogetTemplate = function(){
          if(scope.direction === "horizontal")
          {
              return "horizontal.html";
          }
          return "vertical.html";
      }
  },
  template: `
    <div class="form-group row">
      <label class="col-2 col-form-label">{{label}}</label>
      <div class="col-10" ng-switch="type">
        <div ng-switch-when="json">
          <textarea class="form-control" name="{{name}}"">{{value}}</textarea>
        </div>

        <textarea ng-switch-when="textarea" class="form-control" name="{{name}}"">{{value}}</textarea>

        <input ng-switch-default class="form-control" type="{{type}}"  ng-required="{{required}}"  placeholder="{{placeholder}}" value="{{value}}" name="{{name}}">

      </div>
    </div>
    <label></label>
  `,
}); 





app.tags.bind('cols', {
  restrict: 'E',
  transclude: true,
  template: `
    <div style="display: flex" ng-transclude>
    </div>
  `
});  




app.tags.bind('list', {
  restrict: 'E',
  compile: function(el, attrs) {
    el.addClass('inxio-list')          
  },
});  



app.tags.bind('card', {
    restrict: 'E',
    transclude: {
        'header': '?header',
        'section': '?section',
        'footer': '?footer'
      },
    controller: ['$scope','$element','$q',function ($scope,$element,$q) {
      this.open = true
      this.toogle = function(src) {
        //$element.find('.card-block').toggle(50)
        this.open = !this.open
      }  

    }],
    link: function(scope, element, attrs, ctrl, transclude) {
        ctrl.open = attrs.open!='false'
        scope.hasHeader = transclude.isSlotFilled('header');
        scope.hasSection = transclude.isSlotFilled('section');
        scope.hasFooter = transclude.isSlotFilled('footer');
        scope.isCustom = (!scope.hasSection && !scope.hasHeader)
    },
    controllerAs: 'card', 
    template:  `
        <div class="card" >
            <div class="card-header" ng-if="hasHeader" >
                <ng-transclude ng-transclude-slot="header"></ng-transclude>
            </div>
            <div class="card-block" ng-if="hasSection && card.open">
               <ng-transclude ng-transclude-slot="section"></ng-transclude>
            </div>
            <div class="card-block" ng-if="isCustom">
               <ng-transclude></ng-transclude>
            </div>
            <div class="card-footer" ng-if="hasFooter && card.open" >
                <ng-transclude ng-transclude-slot="footer"></ng-transclude>    
            </div>
        </div>
    `
});



app.tags.bind('tabs', {
  restrict: 'E',
  scope: {},
  transclude: true,
  controller: function () {
  	this.tabs = [];
    this.addTab = function addTab(tab) {
    	this.tabs.push(tab);
    };
    this.selectTab = function selectTab(index) {
      for (var i = 0; i < this.tabs.length; i++) {
        this.tabs[i].selected = false;
      }
    	this.tabs[index].selected = true;
    };
  },
  controllerAs: 'tabs',
  link: function ($scope, $element, $attrs, $ctrl) {
  	$ctrl.selectTab($attrs.active || 0);
  },
  template: `
  	<div class="tabs">
    	<ul class="tabs__list nav nav-pills">
      	<li ng-repeat="tab in tabs.tabs" class="nav-item">
        	<a href="" class="nav-link" data-toggle="pill" ng-bind="tab.label" ng-click="tabs.selectTab($index);"></a>
        </li>
      </ul>
    	<div class="tabs__content" ng-transclude></div>
    </div>
  `
})


app.tags.bind('tab', {
  restrict: 'E',
  scope: {
  	label: '@'
  },
  require: '^tabs',
  transclude: true,
  template: `
  <div class="tabs__content" ng-if="tab.selected">
  	<div ng-transclude></div>
  </div>`,
  link: function ($scope, $element, $attrs, $ctrl) {
  	$scope.tab = {
    	label: $scope.label,
    	selected: false
    };
  	$ctrl.addTab($scope.tab);
  }
})









