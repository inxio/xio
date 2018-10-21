(function() {


    try
    {
        Function("() => {};"); 
        window.xio_ES6 = true
    }
    catch(exception)
    {
        window.xio_ES6 = false
    }

    window.xio_sdk_bootstrap = true;

    

    // SET xio_sdk_baseurl
    var baseurl = document.currentScript.src
    var l = baseurl.split('/');

    var n = l.pop();
    if (n=='bootstrap.js') {
        window.xio_sdk_baseurl = l.join('/')
        var scripts = [
            'lib/jquery-3.3.1.min.js',
            'lib/mustache.min.js',
            'lib/webcomponents-lite.js',
            "lib/nacl-fast.min.js",
            "lib/nacl-util.min.js",
            "lib/sha256.min.js",
            "lib/2.5.3-crypto-md5.js",
            "core/xio.js",
            "core/xio.network.handler.js",
            "core/xio.network.js",
            "core/xio.user.js",
            'core/xui.js',
            'components/core.js',
            'components/tags.js',
        ]
    } else if (n=='xio.min.js') {
        l.pop();
        window.xio_sdk_baseurl = l.join('/')
        var scripts = []
    }

    // SET app_baseurl
    //var baseurl = document.location.origin
    var l = document.location.pathname.split('/');
    l.pop();
    window.xio_app_basepath = l.join('/')


    // core requirements
    /*
    (function() {
      if ('registerElement' in document
          && 'import' in document.createElement('link')
          && 'content' in document.createElement('template')) {
        // platform is good!
      } else {
        // polyfill the platform!
        var e = document.createElement('script');
        e.src = '/bower_components/webcomponentsjs/webcomponents-lite.min.js';
        document.body.appendChild(e);
      }
    })();
    */

    var css = [
        'css/sdk.css',
        'lib/fontawesome4/font-awesome.min.css',
    ]


    // loading

    for (var i in scripts) {
        document.write('<script type="text/javascript" src="'+xio_sdk_baseurl+'/'+scripts[i]+'"></script>');
    }

    for (var i in css) {
        document.write('<link rel="stylesheet" href="'+xio_sdk_baseurl+'/'+css[i]+'">');
    }


})();
