
var inxio_bootstrap = true; // auto rendering 


var baseurl = document.location.origin
var l = document.location.pathname.split('/');
l.pop();
var basepath = l.join('/')

// core requirements

var scripts = [
    'sdk/lib/jquery-3.3.1.min.js',
    'sdk/lib/webcomponents-lite.js',
    'sdk/lib/mustache.min.js',
    'sdk/core/ihm.js',
    //'app.js'
]

var css = [
    'sdk/lib/fa/css/font-awesome.min.css',
]

//  css

css.push('sdk/css/app.css')
css.push('sdk/css/skin.css')

// loading

for (var i in scripts) {
    document.write('<script type="text/javascript" src="'+basepath+'/'+scripts[i]+'"></script>');
}

for (var i in css) {
    document.write('<link rel="stylesheet" href="'+basepath+'/'+css[i]+'">');
}

