
(function(){

	function _sort(iso,key) {
		return function(el) {
			return iso.sortHandler(key,el)
		}
	}

	AppIsotope = function(id,config) {
        if (typeof id === 'string' || id instanceof String) {
		    console.log('create iso from id #'+id)
            this.id = id;
            this.container = document.getElementById(this.id);
        } else {
            console.log('create iso from element'+id)
            this.container = id;
        }
		
		this.data = {}
		this.config = config || {}
        if (!this.config['itemSelector'])
		    this.config['itemSelector'] = '.item'

        if (this.config['itemTemplate'])
            this.template = this.config['itemTemplate']

		//this.config['masonry'] =  {columnWidth: '.item-sizer'}

        if (this.config['data']) {
		    // dyn sort data

		    var datasort = this.config['data']['sort'];
		    this.config['getSortData'] = {};
		    for (i in datasort) {
			    var key = datasort[i];
			    //console.log(i+' '+key)
			    this.config['getSortData'][key] = _sort(this,key)
		    }
		    //this.config['getSortData'] = getSortData;
        }

		//console.log('container =  '+this.container)
		//console.log('config =  '+ JSON.stringify(this.config))
		
		/*
		getSortData:{
			title: '[data-title]',
			rating: function( e ) { 
			  return parseInt( $(e).data('rating') );
			},
		}
		*/
		this.current_xhr = null
		this.iso = new Isotope( this.container, this.config)
        if (!this.template) {
		    this.template = $(this.container).find('.iso-default-template').html()
		    $(this.container).find('.iso-default-template').remove()
        } 
		return this
	}
	AppIsotope.prototype = {


        setView: function(view) {
            $(this.container).addClass('view view-'+view)
        },

		sortHandler: function(key,el) {
			//console.log('default sort by '+key)
			var id = $(el).data('id')	
			//var value =  parseInt( this.data[id][key] )
			if (this.data[id]) {
				var value =  this.data[id][key] 
				//console.log('default sort by '+key+' '+id+' '+value)
			}
			return value;	
		},

		fill: function(data) {
			console.log('iso fill ')

			var template = this.template[0]
			var html = Mustache.to_html(this.template,data);
			//console.log(html)
			$(this.container).html(html);
			this.iso = new iso(this.container, this.config);
		},

		push: function(data) {
            // cas d'un html
            if (typeof data === 'string' || data instanceof String) {
                var html = data
			    //console.log('iso push html'+html)
                var els = $.parseHTML(html.trim())
                this.iso.insert( els ) 
                
                return
            }

			//console.log('iso push data'+data.length)

			var template = this.template
			for(var i in data) {
				
   				var html = Mustache.to_html(template,data[i]);
				//console.log('iso push '+html)
				var els = $.parseHTML(html.trim())
				for (j in els) {
					var id = $(els[j]).data('id')
					
					if (!id) {
						var id = Object.keys(this.data).length
						//console.log('autoid '+id)
						$(els[j]).data('id', id)
					}
					this.data[id] = data[i]
				}
				
				this.iso.insert( els ) 
			}
			return
		},

		filter: function(key,val,callback) {

            if (typeof val === "function") {
                callback = val;
                val = undefined;
            }

			if (callback) {
				this.iso.once( 'layoutComplete', callback )
			}
			
            if (val!=undefined) {
                //console.log('iso apply filter '+key+' = '+val)	
			    this.iso.arrange({ filter: function() {
				    return (val==$(this).data(key))
			    }});
            } else {
                //console.log('iso apply filter '+key)	
			    this.iso.arrange({ filter: key});
            }
		},

        hide: function($items) {
            var els = [];
            var self = this
            $items.each(function() {
                els.push( self.iso.getItem($(this)[0]) );
                //self.iso.hide( self.iso.getItem($(this)[0]) )
            });
            //console.log(els)    
            //console.log(this.iso.getItem(els))   
            this.iso.hide( els )

        },

        remove: function(target) {
            if (typeof target === 'string' || target instanceof String) {
                target = $(this.container).find(target) 
            }
            //console.log('iso removing',target)
            this.iso.remove( target)   
			this.iso.layout();	 
        },

		sort: function(key,asc) {
			if (asc==null) asc = true 
			//console.log('iso sorting by '+key+' '+asc)	
			this.iso.arrange({
				sortBy:key,
				sortAscending: asc
			})
		},

		refresh: function(callback) {

			if (callback) {
				this.iso.once( 'layoutComplete', callback )
			}
			this.iso.layout();
		},

		clear: function(callback) {
			this.iso.remove( $('.item:not(.isoheader)') )
			if (callback) {
				this.iso.once( 'layoutComplete', callback )
			}
			this.iso.layout();	
			this.start = null
		},

		
		load: function(extraparams,callback) {
			this.iso.remove( $( this.container ).find('.loader') )
			if(typeof extraparams == "function") {
				callback = extraparams
				extraparams = {}
			}

			var params = params || {}
			var datasource = this.config['data']['datasource']
			var params = this.config['data']['params'] || {}
			for (key in extraparams) {
				params[key] = extraparams[key]
			}
			var limit = this.config['data']['limit']
			if (this.start == null) {
				this.start = 0	
			} else {	
				this.start += 1
			}
			params['limit'] = limit
			params['start'] = this.start*limit

			//console.log('iso loading '+datasource+' '+JSON.stringify(params))
			if (this.current_xhr) {
				//console.log('iso must abort last request !!!'+this.current_xhr)
				this.current_xhr.abort();
			}

			var iso = this
			this.current_xhr = app.get(datasource,params,function(data) {
				iso.current_xhr = null
				//console.log('iso loaded data '+data.length+' on '+limit)
				iso.push( data )	
				if (data.length==limit) { 
					iso.datanext = true
					var elem = $('<div class="item loader"></div>').click(function(){ 
						
						iso.load() 
					})
					$( iso.container ).append( elem )
					iso.iso.appended( elem ) 	// $("<div></div>");
				} else {
					iso.datanext = false
				}

				iso.iso.updateSortData( iso.config['itemSelector'] )
				if (callback) {
					callback()
				}
			})
		},


        selectItem: function(item) {
            console.log('iso.selectitem')
            item.addClass('selected')
            this.filter('.selected') 
            this.iso.layout()
            this.onSelectItem(item)
        },
        onSelectItem: function(item) {
            console.log('iso.onSelectItem')
        }, 

        unSelectItem: function(item) {
            console.log('iso.unSelectitem')
            item.removeClass('selected')
            this.filter() 
            this.iso.layout()
            item.parent().nextAll().remove()
            this.onUnSelectItem(item)
        },
        onUnSelectItem: function(item) {
            console.log('iso.onUnSelectItem')
        }, 
        

        enhance: function() {


            //$(this.container).enhance() // app enhance ?

            var target = $(this.container)
            var self = this
            console.log('enhance iso')

            $(target).find('.item .cover').unbind('click').bind('click', function(event) { 
                var item = $(this).closest('.item')
                if (item.hasClass('selected')) {
                    self.unSelectItem(item)    
                } else {
                    self.selectItem(item)  
                }
            })

            $(target).find('*[data-iso-select]').unbind('click').bind('click', function(event) { 

                // check a@href
                var href = $(event.target).attr('href')
                if (!href) {
                

                    if ( $(this).hasClass('item') ) {
                        var item = $(this)
                    } else {
                        var item = $(this).closest('.item') 
                    }
                    var selected = $(item).hasClass('selected') 
                    var callbackname = $(this).data('iso-select')
                    //console.log('callbackname',callbackname)   
                    var callback = window[callbackname]
                    //console.log('callback',callback) 
                    if (selected) {
                        $(item).removeClass('selected') 
                        $(item).iso().filter()
                        callback(item,false)
                    } else {
                        $(item).addClass('selected').siblings().removeClass('selected') 
                        $(item).iso().filter('.selected')
                        callback(item,true)
                    }
                    return false;
                }
            }),


            $(target).find('*[data-iso-view]').unbind('click').bind('click', function() { 

                var container = $(this).closest('ul')
                var currentview = container.find('.active').data('iso-view') 
                var newview = $(this).data('iso-view')
                container.find('.active').removeClass('active')
                $(this).addClass('active')

                var target = $(this).closest('*[data-iso-target]').data('iso-target')
                if (!target) {
                    var target = $(this).closest('.iso')  
                }
                $(target).removeClass('view1 view2 view3 view3 view4 view5').addClass(newview)
                $(target).iso().refresh()
                return false;
            })

            $(target).find('*[data-iso-filter]').unbind('click').bind('click', function() {
                var cls = $(this).data('iso-filter') 
                var target = $(this).closest('.iso')
                if (!target.length) {
                    var target = $(this).closest('*[data-iso-target]').data('iso-target')
                }
                $(target).iso().filter(cls)
                return false;
            })

        },

	}


})();


$.fn.iso = function(config) {
    var el = this[0]    
    if (config) {
        el._iso = new AppIsotope(el,config)
    } else {
        if (!el._iso) {
            el = this.closest('.isotope')[0]   
        }
    }
    return el._iso

};

   




