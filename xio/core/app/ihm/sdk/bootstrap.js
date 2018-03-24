
var xio_sdk_bootstrap = true; // auto rendering 

/*
alert( document.currentScript.src )
var baseurlxio = document.currentScript.src
var baseurlxio = document.currentScript.src
*/


// SET xio_sdk_baseurl
var baseurl = document.currentScript.src
var l = baseurl.split('/');
l.pop();
var xio_sdk_baseurl = l.join('/')

// SET app_baseurl
//var baseurl = document.location.origin
var l = document.location.pathname.split('/');
l.pop();
var xio_app_basepath = l.join('/')


// core requirements

var scripts = [
    'lib/jquery-3.3.1.min.js',
    'lib/webcomponents-lite.js',
    'lib/mustache.min.js',
    'lib/nacl-fast.min.js',
    'lib/nacl-util.min.js',
    'lib/sha256.min.js',
    'core/xio.js',
    'core/xio.network.js',
    'core/xio.user.js',
    'core/ihm.js',
]

var css = [
    'lib/fa/css/font-awesome.min.css',
]


// loading

for (var i in scripts) {
    document.write('<script type="text/javascript" src="'+xio_sdk_baseurl+'/'+scripts[i]+'"></script>');
}

for (var i in css) {
    document.write('<link rel="stylesheet" href="'+xio_sdk_baseurl+'/'+css[i]+'">');
}

