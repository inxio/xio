(function(){


    app.services.bind('ipfs',{
	    handler: 'xrn:inxio:ipfs'
    })

    app.nav.links.bind('ipfs',{
        handler: function(value,element) {
        	return 'https://ipfs.io/ipfs/'+value
            alert(link)	
            //element.attr('href')
            app.services.ipfs.get('ipfs/'+link).then( function(data) {
            	alert(data)
            })
        }
    })



	Ipfs = function() {
        console.log('init Ipfs ')
        this.gateway = 'http://127.0.0.1:8080/'
		return this;
	};


	Ipfs.prototype = {

        get: function(ipfshash) {
            var url = this.gateway+'ipfs/'+ipfshash
            console.log(url)
            return $.get(url)
        },
       
    }

})();


