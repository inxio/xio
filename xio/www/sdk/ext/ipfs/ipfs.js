(function(){

    /*
    app.services.bind('ipfs',{
	    handler: 'xrn:inxio:ipfs'
    })

    app.nav.links.bind('ipfs',{
        handler: function(value,element) {
        	return 'https://ipfs.io/ipfs/'+value
            //element.attr('href')
            app.services.ipfs.get('ipfs/'+link).then( function(data) {
            })
        }
    })
    */
    xio.handlers.bind('ipfs',function(uri) {
        alert(uri)
    })


	Ipfs = function() {
        app.log.debug('init Ipfs ')
        //this.gateway = 'http://127.0.0.1:5000/'
        // https://github.com/pelle/browser-ipfs
        this.connector = ipfs
        //this.connector.setProvider({host: 'localhost', port: '5001'})
        // https://ipfs.infura.io:5001
        this.connector.setProvider()
        this.db = new XioDb('inxio-ipfs')
        this.cache = {} // promises caching
		return this;
	};




	Ipfs.prototype = {

        get: function (hash) {
            var self = this
            hash = $.trim(hash)
            if (!hash)
                return $.Deferred().resolve({})

            if (hash[0]!='Q') {
                xio.log.warning('IPFS WARNING WRONG HASH : '+hash)
                return $.Deferred().resolve({})
            }

            // check cache ipfs
            var result = this.db.get(hash)
            if (result) {
                xio.log.debug('IPFS WARNING WRONG HASH : '+hash)
                return $.Deferred().resolve(result).promise()
            }
            return this.cat(hash).then( function(content) {
                var result = JSON.parse(content);
                self.db.put(hash,result);
                return result
            })
        },
        put: function (content) {
            if (!content || $.isEmptyObject(content))
                return $.Deferred().resolve('').promise()
            var content = JSON.stringify(content)
            return this.add(content)
        },


        cat: function(ipfshash) {
            if (!this.cache[ipfshash]) {
                var d = $.Deferred(); 
                this.connector.cat(ipfshash, function(err, content) {
                    if (err)
                        d.reject( err )
                    else
                        d.resolve( content )
                });
                this.cache[ipfshash] = d.promise()
            }
            return this.cache[ipfshash]
        },
        add: function(content) {
            var d = $.Deferred(); 
            this.connector.add(content, function(err, hash) {
                if (err)
                    d.reject( err )
                else
                    d.resolve( hash )
            });
            return d.promise()
        },
    }

})();


