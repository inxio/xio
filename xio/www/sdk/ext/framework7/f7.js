(function(){

    window.F7 = function() {
        console.log('init framework7 ')
        this.f7app = new Framework7({
          root: '#app', 
          name: 'Framework7', // App name
          theme: 'auto', // Automatic theme detection
          data: function () {
            return {
              user: {
                firstName: 'John',
                lastName: 'Doe',
              },
            };
          },
          methods: {
            helloWorld: function () {
              app.dialog.alert('Hello World!');
            },
          },
          //'router': false,
          'routes': [
            {
              path: '/p1/',
              pageName: 'p1',
            },
            {
              path: '/p2/',
              pageName: 'p2',
            },
            {
              path: '/home/',
              pageName: 'home',
            },
            {
              path: '#debug',
              pageName: 'debug',
            },
          ],
          clicks: {
            //externalLinks: 'a',
          }
        });
        this.$$ = Dom7;
        this.mainView = this.f7app.views.create('.view-main', {
          url: '/'
        });

        this.searchbar = this.f7app.searchbar
        this.currentPage = this.mainView.activePage
        this.currentPageHandler = null
        this.currentPageQuery = {} //this.mainView.activePage.query
        this.currentPageTab = null

        var self = this
        //this.f7app.onPage('*', function (page){ console.log('onpage') } );
        //this.f7app.onPageBeforeAnimation('*', function (page){ console.log('onPageBeforeAnimation') } );
        //this.f7app.onPageInit('*', function (page) { self.onInitPage(page) } );
        //this.f7app.onPageReinit('*', function (page) { self.onShowPage(page) } );
    };

    F7.prototype = {

        refreshPage: function(query,clear_query) {
            console.log('=====refresh==',query,clear_query)
            console.log('=====refresh page==',this.currentPage)
            console.log('=====refresh page old query==',this.currentPageQuery)
            var page = this.currentPage
            var content = $(page.container).find('.page-content') 
            if (clear_query) {
                var currentId = this.currentPageQuery['id']
                this.currentPageQuery = {
                    'id': currentId // fix pb search companies vs search company
                }   
            }
            for (key in query) {
                this.currentPageQuery[key] = query[key]       
            }
            console.log('=====refresh page new query==',this.currentPageQuery)
            this.currentPageHandler.call(this,page,this.currentPageQuery,content);
        },

        showPage: function(url) {

            console.log('showPage '+url)

            this.f7app.mainView.router.load({
                url: url, 
                ignoreCache: true, 
                reload: true
            });

            // test bug tab business
            var self = this
            this.$$('.tab').on('tab:show', function(e) { self.onShowTab(e) } );      
        },

        showTab: function(tabid) {
            console.log('showTab '+tabid)
            var tabname = tabid.slice(4);
            var funcname = 'onShowTab'+tabname[0].toUpperCase() + tabname.slice(1);
            try {
                var handler = window[funcname]
                var content = $('#'+tabid+' .tab-content')
                if (!content.length )
                    var content = $('#'+tabid)
                handler.call(this,this.currentPage,this.currentPageQuery,content);
            } catch (e) {
                console.log('onShowTab ERROR '+funcname+' '+e)
            }  
        },

        onShowTab: function(e) { 
            console.log('onShowTab ...',e.target.id); 
            console.log('onShowTab ... ctx',this.currentPageQuery); 
            if (e.target.id) {
                // custom event f7
                var tabid = e.target.id
                var param = $(e.srcElement).data('ihm-param')
            } else {
                // event js
                var tabid = $(e.target).attr('href').slice(1)
                var param = $(e.target).data('ihm-param')
            }
            this.currentPageQuery['param'] =  param   
            this.currentPageTabId = tabid   

            var tabname = tabid.slice(4);
            var funcname = 'onShowTab'+tabname[0].toUpperCase() + tabname.slice(1);
            try {
                var handler = window[funcname]
                var content = $('#'+tabid+' .tab-content')
                if (!content.length )
                    var content = $('#'+tabid)

                handler.call(this,this.currentPage,this.currentPageQuery,content);
            } catch (e) {
                console.log('onShowTab ERROR '+funcname+' '+e)
            }
        },

        onInitPage: function(page) { 
            console.log('onInitPage ...',page.name); 
            var self = this
            this.$$('.tab').on('tab:show', function(e) { self.onShowTab(e) } );  
            this.onShowPage(page)
            app.enhance( $(page.container) )
            console.log(app.enhance)
            console.log('onInitPage ...',page.name,'done'); 
        },

        onShowPage: function(page) { 
            // https://framework7.io/docs/pages.html
            console.log('onShowPage ...',page.name); 

            var pagename = page.name
            var funcname = 'onShowPage'+pagename[0].toUpperCase() + pagename.slice(1);
            try {
                var handler = window[funcname]
                var content = $(page.container).find('.page-content')

                this.currentPage = page
                this.currentPageHandler = handler
                this.currentPageQuery = page.query

                handler.call(this,page,page.query,content);


                var searchBar = this.searchbar('.searchbar', {
                    customSearch: true,
                    onSearch: function(s) {
                        if (s.query.length>=3) {
                            app.onSearchEdit(s.query)
                        }
                    },
                    onClear: function(s) {
                        console.log('Clearing', s);
                        this.refreshPage({})
                    }
                });

                $(".searchbar input").on('keyup', function (e) {
                    if (e.keyCode == 13) {
                        app.onSearch(this.value)
                    }
                });



            } catch (e) {
                console.log('onShowF7 ERROR '+funcname+' '+e)
            }
        }
    };

})();
