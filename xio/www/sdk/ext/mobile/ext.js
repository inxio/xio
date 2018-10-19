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




app.tag('xio-app').type('mobile').bind( class {

    init(el) {
        this.el = el
    }

    render() {
        alert('mobile render !!!')
    }

    getTemplate() {
        return `
          <div class="c-offcanvas-content-wrap">
            
              <header >
                      <nav class="navbar navbar-dark bg-dark fixed-top">
                               <button type="button" class="btn btn-outline-secondary" >Primary button</button>
                              <a class="navbar-brand" href="#">
                                  <img src="sdk/images/icon.png" height="36" class="d-inline-block align-top" alt="" > {{app.about.name}} 
                              </a>
                              <button type="button" class="btn btn-outline-secondary"  >Primary button</button>
                      </nav>
               </header>



                  <section id="page1">  

                     <div class="jumbotron">
                        <h1 class="display-4">Hello, world!</h1>
                        <p class="lead">This is a simple hero unit, a simple jumbotron-style component for calling extra attention to featured content or information.</p>
                        <hr class="my-4">
                        <p class="lead">
                          <a class="btn btn-primary btn-lg" href="#" role="button">Learn more</a>
                        </p>
                      </div>

                  </section>

                  <section id="page2" style="display:none">  

                     <div class="jumbotron">
                        <h1 class="display-4">page2!</h1>
                        <p>It uses utility classes for typography and spacing to space content out within the larger container.</p>

                      </div>

                  </section>

                  <section id="page3" style="display:none">  

                     <div class="jumbotron">
                        <h1 class="display-4">page2!</h1>
                        <p>It uses utility classes for typography and spacing to space content out within the larger container.</p>

                      </div>

                  </section>



                  <footer >
                      <nav  class="navbar fixed-bottom navbar-dark bg-dark">

                      
                      
                          <ul class="nav nav-pills nav-fill" style="width:100%" >
                            <li class="nav-item">
                              <a class="nav-link active" data-toggle="pill" href="#page1">Active</a>
                            </li>
                            <li class="nav-item">
                              <a class="nav-link" data-toggle="pill" href="#page2">Longer nav link</a>
                            </li>
                            <li class="nav-item">
                              <a class="nav-link" data-toggle="pill" href="#page3">Link</a>
                            </li>

                          </ul>
                      
                      </nav>
                  </footer>



          </div>

              <!--Left-->
              <aside class="js-offcanvas" id="offCanvas" style="z-index: 20000" role="complementary">
                <div class="c-offcanvas__inner o-box u-pos-relative">
                    <ul class="c-menu c-menu--border u-unstyled">
                      <li class="c-menu__item c-menu__item--heading">Header</li>
                      <li class="c-menu__item"><a class="c-menu__link" href="#nogo">Home</a></li>
                      <li class="c-menu__item"><a class="c-menu__link" href="#nogo">About</a></li>
                      <li class="c-menu__item"><a class="c-menu__link" href="#nogo">Portfolio</a></li>
                      <li class="c-menu__item"><a class="c-menu__link" href="#nogo">Projects</a></li>
                      <li class="c-menu__item"><a class="c-menu__link" href="#nogo">Contact</a></li>
                  </ul>
                </div>
              </aside>

          `;
    }
    

    
})


app.tag('xio-app').on('rendered', function() {
    alert('rendered xio app')
})



$(document).ready( function() {

    $('section').click(function() {
        $('.navbar').slideToggle(150);
    })

    $('footer a').click(function() {
        $('#page1, #page2').slideToggle(150);
    })
})


/*
https://github.com/vmitsaras/js-offcanvas
*/

$(document).ready( function() {

    $('#offCanvas').offcanvas({
        modifiers: 'left, overlay',
        triggerButton: 'header button', 
        modal: true,
    });

});