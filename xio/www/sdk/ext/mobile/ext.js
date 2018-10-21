/*
$(window).scroll(function () {

         // set distance user needs to scroll before we start fadeIn
    if ($(this).scrollTop() > 100) {
        $('.navbar').fadeIn();
    } else {
        $('.navbar').fadeOut();
    }
});
*/


app.tag('xio-app').on('rendered', function() {
    console.log('test on.rendered xio app')
})




app.tag('xio-app').type('mobile').bind( class {

    init(el) {
        this.el = el
    }

    render() {
        console.log('mobile render !!!')


      $('div.main').click(function() {
          $('.navbar.primary').slideToggle(150);
      })

      // hook xio-page animation
      
      app.tag('xio-page').handler.prototype.hide = function() {}
      app.tag('xio-page').handler.prototype.show = function() {
        var previd = app.nav.curentPageId
        var newid = this.id
        if (previd) {
          $('#'+previd+', #'+newid).slideToggle(150);
        }
        else {
          $(this).show()
        }
        app.nav.curentPageId = this.id
        //alert('sho page'+this.id) 
      }

      /*
      $('footer a').click(function() {
          $('#page1, #page2').slideToggle(150);
      })
      */

      $('header button.panel-left').click(function() {
          $("#panel-left")[0].open()
      })    
      $('header button.back').click(function() {
          window.history.back()
      }) 
      $('header button.panel-right').click(function() {
          $("#panel-right")[0].open()
      })
    }

    getTemplate() {
        return `
          <div class="c-offcanvas-content-wrap">
            
              <header class="fixed-top">
                      <nav class="navbar navbar-dark bg-dark primary">
                               <button  type="button" class="btn btn-outline-secondary panel-left" >Primary button</button>
                               <xio-button class="btn-outline-secondary panel-left" icon="bars"></xio-button>
                              <a class="navbar-brand" href="#">
                                  <img src="sdk/images/icon.png" height="36" class="d-inline-block align-top" alt="" > {{app.about.name}} 
                              </a>
                              <button type="button" class="btn btn-outline-secondary panel-right"  >Primary button</button>

                      </nav>
                      <nav class="navbar navbar-light bg-light " style="display:none">
                               <button  type="button" class="btn btn-outline-secondary back" >Back</button>
                              <a class="navbar-brand" href="#">
                                  page 
                              </a>
                              
                      </nav>
               </header>


              <div class="main" style="padding-top: 100px; padding-bottom: 100px;" >  

                  <xio-page id="login">
                      landing
                      <xio-onboarding>
                      </xio-onboarding>
                  </xio-page>

                  {{#app.nav.sitemap}}
                      <xio-page id="{{id}}" src="{{src}}" template="{{template}}" data="{{data}}">
                        content of {{id}}
                      </xio-page>
                  {{/app.nav.sitemap}}

                  <div class="slot">
                  </div>

              </div>




                  <footer >
                      <nav  class="navbar fixed-bottom navbar-dark bg-dark primary">
                          <ul class="nav nav-fill" style="width:100%" >
                            {{#app.layout.slot.footer-nav.links}}
                              <li class="nav-item"><a class="nav-link" href="{{path}}" >{{label}}</a> </li> 
                            {{/app.layout.slot.footer-nav.links}}
                          </ul>
                      
                      </nav>
                  </footer>



          </div>

              <xio-panel id="panel-left" class="panel-left">

                <nav class="list-group">
                  {{#app.layout.slot.panel-left.links}}
                    <a href="{{path}}" class="list-group-item list-group-item-action ">
                      <i class="fa fa-lg fa-remove float-right" style="color: red;">></i>
                      {{label}}
                    </a>
                  {{/app.layout.slot.panel-left.links}}

                </div>
              </nav>

              </xio-panel>

              <xio-panel id="panel-right" class="panel-right">
                hello
              </xio-panel>

          `;
    }
    

    
})


/*
https://github.com/vmitsaras/js-offcanvas
*/

app.tag('xio-panel').bind( class extends XIOElement {

    init() {
        $(this).addClass('js-offcanvas')
        $(this).css('z-index','20000')

        if ($(this).hasClass('panel-right')) {
          this.direction = 'right'
        } 
        if ($(this).hasClass('panel-left')) {
          this.direction = 'left'
        } 
        
        $(this).offcanvas({
            modifiers: this.direction+', overlay',
            triggerButton: 'header button.panel-'+this.direction, 
            modal: true,
        });

    }

    getTemplate() {
        return `<aside>
          <header>
                <nav class="navbar navbar-dark bg-dark ">
                        {{#panelRight}}<button type="button" class="btn btn-outline-secondary closepanel"  >X</button>{{/panelRight}}
                        <a class="navbar-brand" href="#">
                            <img src="sdk/images/icon.png" height="36" class="d-inline-block align-top" alt="" > {{app.about.name}} 
                        </a>
                        {{#panelLeft}}<button type="button" class="btn btn-outline-secondary closepanel"  >X</button>{{/panelLeft}}
                </nav>
          </header>

          <div class="slot">

          </div>

          <footer>
          
          </footer>

        </aside>
        `;
    }

    getData() {
      return {
        panelRight: $(this).hasClass('panel-right'),
        panelLeft: $(this).hasClass('panel-left'),
      }
    }
    open() {
      $(this).data('offcanvas-component').open()
    }
    close() {
      $(this).data('offcanvas-component').close()
    }

    render() {
        var self = this
        return super.render().then( function() {

          $(self).find('button.closepanel').click(function() {
              self.close()
          })

          $(self).find('a').click(function() {
              self.close()
          })

        })
    }
    
})




