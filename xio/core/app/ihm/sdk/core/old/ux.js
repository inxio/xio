

var template_header = null
var template_item = null
var template_item_header = null

/*
var currentpath = ''
var currentData = null
var currentIsoChildren = null
*/

var currentIso = null
var currentIsoChildren = null
var currentResource = null

var navstack = []
var stack = []

$(document).ready(function() {

    template_item = $('#template-item').text()
    template_item_header = $('#template-item-header')

})

function testEndpoint() {
    var url = location.protocol+'//'+location.host+getFullPath()
    window.open(url,"_new")
}

function doLabAction(action,el) {

    if (action=='addContainer') {
        addContainer(el) 
    }
    if (action=='addContainerItem') {
        addContainerItem(el) 
    }

    if (action=='pin') {
        var name = getPath().replace(/\//g,'-')
        var path = name
        var unpin = currentResource['linked']
        

        if (unpin) {
            app.delete(path,data).then(
                navto('/')
            )  
            
        } else {
            
            var data = {
                'name': name,
                'type': currentResource['type'],   
                'icon': currentResource['icon'],   
                'linked': getPath(),
            }
            app.put(path,data).then(
                navto('/')
            )    
        }
        

    }



    if (action=='delete') {

        dialogConfirm({
            'header': 'Suppression ?',
            'body': 'Confirmez vous la suppression',
            'callback': function() {
                var path = getPath()    
                app.delete(path).then( function (data) {
                    navto('..')
                })
            }
        })
        return false
    } 


    return false;
}




function getFullPath(path) {
    return '/'+session.aid+'/'+getPath(path); 
}

function getPath(path) {
    path = path || ''    
    var basepath = navstack.join('/');
    if (path) 
        if (basepath)
            return basepath+'/'+path;
        else
            return path
    else
        return basepath;
}



function clearRootContainer() {  
    //return $('#rootcontainer').html('')    

    $('#rootcontainer').children().each( function(){
        var ciso = $(this)
        $(this).iso().clear( function() {
            ciso.remove()
        })
    })
    
}




/*

OLD 

*/

function uxToogle(action,el) {

    var actived = $(el).hasClass('active')

    var callback = function() {
            if (actived)    { $(el).removeClass('active') }
            else            { $(el).addClass('active') }
    }
    if (action=='fullscreen') {
        if (screenfull.enabled) {

            if (actived) {
                $(el).find('span').removeClass('fa-compress').addClass('fa-expand')
            } else {
                $(el).find('span').removeClass('fa-expand').addClass('fa-compress')
            }
            screenfull.toggle();
            callback()
        }
    }
    if (action=='debugcss') {
        
        if (actived) {
            $('body').removeClass('debug-enabled');
            app.log = function() {}
        } else {
            $('body').addClass('debug-enabled');
            app.log = app.log
        }
        callback()
    }
    if (action=='websocket') {
        
        if (actived) {
            initApp('http')
        } else {
            initApp('ws')
        }
        callback()
    }
}






function submitContainerSelection(form) {
    var keyword = $(form).find('*[name=keyword]').val()
    alert(keyword)    
    params = {
        'keyword': keyword
    }
    showServiceInfo('.home',null,params)
}

     



function showServiceInfo(infotype,callback,params) {

    app.log(infotype)

    var params = params || {}

    var renderViewJson = function(resp) {

        var context = currentResource['context']
        var data = resp['content']

        var template = $('#template-schema')
        var html = template.render({'html':json2html(data)})
       
        currentIsoChildren.clear()
        currentIsoChildren.push(html)
        $(currentIsoChildren.container).clean()
        if (callback) { callback() }
    }

    var renderViewSchema = function(resp) {

        var context = currentResource['context']
        var data = resp['content']

        var template = $('#template-schema-'+context)
        if (template.length) {    
            var html = template.render(data)
        } else {
            var template = $('#template-schema')
            var html = template.render({'html':json2html(data)})
        }
        currentIsoChildren.clear()
        currentIsoChildren.push(html)
        $(currentIsoChildren.container).clean()
        if (callback) { callback() }
    }

    var renderViewHtml = function(resp) {
        var data = resp['content']

        $(data).each( function(index,val) {
            data[index] = fixAbout(val,true)
        })
        currentIsoChildren.clear()

        if (getPath()=='services') {
            var template = $('#template-iso-header')
            var html = template.render(currentResource)
            currentIsoChildren.push(html)
        }
        currentIsoChildren.push(data)

        if (currentResource['options'] && currentResource['options']['PUT']) {
            var template = $('#template-item-add')
            var html = template.render(currentResource['ihm']['add'])
            currentIsoChildren.push(html)
        }

        $(currentIsoChildren.container).clean()

        if (callback) { callback() }
    }

    var renderView = function (resp) {

        var data = resp
        if (typeof data['content'] != 'string')
            data['content'] = JSON.stringify(data['content'], undefined, 4);

        var template = $('#template-item-content')
        var html = template.render(data)
        currentIsoChildren.clear()
        currentIsoChildren.push(html)
        $(currentIsoChildren.container).clean()
    }



    var viewcallback = renderView

    // gestion .view.{{name}}
    var view = null
    var check = infotype.split('.');
    if (check.length>2) {   
        infotype = '.content'
        view = check[2]
    }

    //app.log('show '+infotype,callback)    

    $(currentIsoChildren.container).closest('.packery').nextAll().remove()

    var toolbar = $(currentIsoChildren.container).prev().find('.item-toolbar')
    var pill = toolbar.find('*[data-select="'+infotype+'"]')
    pill.parent().addClass('active').siblings().removeClass('active')


    if (infotype=='.home') {       

        if (currentResource['type']=='operation') {
            infotype = '.operation'
        } else if (currentResource['type']=='item') {
            infotype = '.content'
        } else {
            infotype = '.content'
            view = 'children'
            viewcallback = renderViewHtml
        }

    }
    if (infotype=='.html1') {  
        infotype = '.content'
        view = 'schema'
        viewcallback = renderViewJson
    }
    if (infotype=='.html2') {  
        infotype = '.content'
        view = 'schema'
        viewcallback = renderViewSchema
    }

    var data = currentResource 

    if (infotype=='_about') { // fix pour voir le about utilisé pour l'ihm
        viewcallback({
            'status': 200,
            'content': data
        })
    }

    if (infotype=='.content') {

        params['xio_view'] = view
        var errback = function(resp) {
            callback(resp)
        }
        
        var url = getPath()    
        app.request('GET',url,params, viewcallback, errback)
    }

    if (infotype=='.containerResponse') {
        var toolbar = $(currentIsoChildren.container).closest('.packery').prev().find('.item-toolbar-specific')
        var keyword = toolbar.find('input[name=keyword]').val()
        var offset = toolbar.find('input[name=offset]').val()
        var limit = toolbar.find('input[name=limit]').val()
        var params = {
            keyword: keyword,
            limit: limit,
            offset: offset,
        }
        var url = getPath('_children')   
        app.get(url,query=params).then( function (data) {  
            alert(data)
        })
        return
    }
    else if (infotype=='.update') {
        var template = $('#template-item-config')
        var html = template.render(data['configuration'])
        currentIsoChildren.clear()
        currentIsoChildren.push(html)
        $(currentIsoChildren.container).clean()
        configurationInit(data)
    }
    else if (infotype=='.operation') {
        if (data['input'] && data['input']['params']) {
            $(data['input']['params']).each( function(index,val) {
                // pb avec value car disparait du formulaire si existe (cas d'une op a moitié configuré coté serveur, dans ce cas ca doit disparaitre de la liste des input de about !)
                //if (val['default']) data['input']['params'][index]['value'] = val['default']    
                if (val['type'])
                    val['ihm_type_'+val['type']] = true    
                else
                    val['ihm_type_text'] = true                 
            })
        }
        //app.log(data)


        operationInit(data)
    }

}






function updateBreadCrumb() {
    // breadcrumb
    
    var breadcrumb = [{
        'name': session.aid,
        'path': '/'+app.session.aid
    }]
    var cpath = []
    for (i in navstack) {
        name = navstack[i]
        cpath.push(name)
        breadcrumb.push({
            'name': name,
            'path': '/'+cpath.join('/')
        })

    }

    var template = $('#breadcrumb-template')
    var html = template.render(breadcrumb)
    $('#breadcrumb').html(html)
    $('#breadcrumb').clean()
}




function fixAbout(about,addnameforimg) { // addname pour le cas des childs

    about['ihm'] = {}

    if (!about['name']) {
        about['name'] = '?nonname?'
        about['hidden'] = true
    }


    about['ihm']['servicecontainer'] = (about['pid']==session.aid+'-1') 
    /*
    if (about['_id']) {
        about['id']=about['_id']
        delete about['_id']
    }
    */
    if (about['pid']=='1')
        about['storeitem'] = true
    if (about['name'][0]=='.') {
        about['hidden'] = true
    }
   
    if (!about['manage']) {
        about['manage'] = {}
    }

    about['path'] = getPath()

    about['endpoint'] = getPath()


    about['ihm'][ 'is'+about['type'] ] = true


    if (about['options'] && about['options']['PUT']) {
        if (about['type']=='app') {
            about['ihm']['add'] = {
                'type': 'instance',
                'label': 'connector',
                'icon': 'fa-plug'
            }
        } else {
            about['ihm']['add'] = {
                'types':  ['folder'],
                'label': 'resource',
                'icon': 'fa-plus-square'
            }
        }
    }
    if (about['options'] && about['options']['PATCH']) {
            about['ihm']['update'] = {
                'label': 'configure',
                'icon': 'fa-gear'
            }

    }

    if (about['output'] && about['output']['context']) {
        about['output']['options'] = [{
            'name': 'schema',
            'context': about['output']['context']            
        }]
    }
            
    return about
}




function onApiSelect(item,selected) {

    var path = $(item).data('item-path') 
    if (path) {
        if (selected) {
            navstack.push(path)
            updateBreadCrumb()
            showItem(item)
        } else {
            hideItem(item)
            updateBreadCrumb()
        }
    }
}  




function hideItem(item) {
    var iso = $(item).iso()
    var container = $(item).closest('.packery')

    $(container).removeClass('focus').prev().addClass('focus')

    iso.remove('.item.header')



    if ( container.nextAll().length!=0 ) {
        container.nextAll().each(function(){
            $(this).remove()
        })
    } 
    
    navstack = navstack.slice(0,1+container.prevAll().length) // 1 = home ou service

    $(item).find('.header-content').fadeOut()
    $(item).removeClass('selected')
    $(container).removeClass('selected') 
    iso.filter( '*') 
}



function showItem(item,callback) {

    // recuperation about
    var url = getPath('_about')

    app.get(url).then( function (data) {
            
            currentResource = fixAbout(data)
            stack.push(currentResource)

            // maj BreadCrumb
            updateBreadCrumb()

            // activation item s'il existe

            if (item) {
                var iso = $(item).iso()
                var container = $(item).closest('.packery')
                

                $(container).addClass('focus').prevAll().removeClass('focus')

                $(item).addClass('selected').siblings().removeClass('selected')

                $(item).find('.header-content').fadeIn()
                //$(container).prevAll().hide(200)
                iso.filter( '.selected' , function () {

                    
                }) 
                $(container).addClass('selected') 

                // gestion toolbar
                var target = $(item).find('.item-toolbar')
                // gestion toolbar génerique 
                var item_toolbar = $('#template-item-toolbar-generic').render(currentResource)
                target.html(item_toolbar)
                target.clean()


                // affichage toolbar specifique
                var specific_template = null
                if (data['type']=='container') { 
                    var specific_template = $('#template-item-toolbar-container') 
                }
                //if (data['type']=='item') { 
                //    var specific_template = $('#template-item-toolbar-item') 
                //}
                if (specific_template) {
                    var html = specific_template.render(data)
                    iso.push(html)
                    $(iso.container).clean()
                }


            }

            // creation container children
            currentIsoChildren = newIso(true)

            // chargement de la home de l'item
            showServiceInfo('.home',callback)

               

        })


    
}




function onShowHome() {
    navstack = []
    clearRootContainer()
    navto('home')
}

function onShowServices() {
    navstack = []
    clearRootContainer()
    navto('services')
}

function navto(path,item,callback) {

    app.log('----------------- NAVTO :',path)
    reload = false    
    if (path=='.') {
        reload = true
        path = ''
        currentIsoChildren.clear()
    } else if (path=='..') {
        path = '/'+navstack.slice(0,-1).join('/'); 
    }    

    var navback = false;
    if (path) {
        if (path[0]=='/') {
            path = path.substring(1)
            if (!path) { // gestion '/'
                navstack = []
                clearRootContainer()
            } else  { 
                navstack = []
                clearRootContainer()
                navto(path)
            } 
            /*
            else { // chemon absolut vers une branche de l'arbre en cours

                return navto('/',false,function(){
                    $('#rootcontainer').find('*[data-navto="'+path+'"]').trigger('click')
                })
                
            }
            */
        } 
    } 

    currentpath = navstack.join('/')

    //app.log('----------------- NAVTO.....',currentpath,'....',path)


    if (!navback) {

        if (item) {
            var selected = $(item).hasClass('selected')
            if (selected) {      
                hideItem(item)
                updateBreadCrumb()
                stack.pop()
                currentResource = stack[stack.length-1]
                $(item).closest('.packery').prev().show(200)
                return
            } else {
                navstack.push(path)
            }
        } else if (path) { 
            navstack.push(path)
        }
    }
    return showItem(item,callback)


}

