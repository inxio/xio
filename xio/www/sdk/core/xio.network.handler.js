(function(){

    function toBytes(str) {
        return web3.fromAscii(str)
    }

    function cleanAddresses(addresses) {
        var cleaned = []
        addresses.forEach(function(address) {
            if (!address.startsWith('0x0000'))
                cleaned.push(address)
        });
        return cleaned;
    }

    BASE_ABI = [
        {
            "constant": true,
            "inputs": [],
            "name": "about",
            "outputs": [
                {
                    "name": "",
                    "type": "string"
                }
            ],
            "payable": false,
            "stateMutability": "view",
            "type": "function"
        }
    ]


    class XioHandler {

        constructor() {
            this._routes = new XioRoutes()
        }

        bind(path,handler) {
            this._routes.bind(path,handler)
        }  

        render(req) {

            var info = this._routes.getHandler(p)

            if (!info) {
                alert('no routes for '+req.path)
                return 
            }

            var handler = info.handler
            var postpath = info.postpath
            var context = info.context
            var req = xio.request(req.method,postpath,req.data,{},context)
            var result = handler.call(this, req)
            
            return $.when(result).then(function(result) {
                return result
            })
        }

    }




    class XioNetworkEthereumHandler extends XioHandler {

        constructor(config) {
            super();  
            var self = this
            this.STATUS_NEW = 0
            this.STATUS_ACTIVE = 1
            this.STATUS_RUNNING = 2
            this.STATUS_PENDING = 3
            this.STATUS_COMPLETED = 9   
            this.PRICING_TYPE_SUBSCRIPTION = 1
            this.PRICING_TYPE_PURCHASE = 2
            this.RESOURCE_TYPE_RESOURCE = 0
            this.RESOURCE_TYPE_NETWORK = 1
            this.RESOURCE_TYPE_USER = 2
            this.RESOURCE_TYPE_SERVICE = 3
            this.RESOURCE_TYPE_OFFER = 4
            this.RESOURCE_TYPE_ORDER = 5
            this.RESOURCE_TYPE_ORDERITEM = 6
            this.TYPE_MAPPING_BY_NAME = {
                'resource': 0,
                'network': 1,
                'user': 2,
                'service': 3,
                'offer': 4,
                'order': 5,
                'orderitem': 6,
            }
            this.TYPE_MAPPING_BY_CODE = {
                0: 'resource',
                1: 'network',
                2: 'user',
                3: 'service',
                4: 'offer',
                5: 'order',
                6: 'orderitem',
            }


            //var uri = config
            this.config = config
            this.uri = config.id
            this.server = config.server

            if (typeof Ipfs === 'function') {
                this.ipfs = new Ipfs()
            }

            if (typeof Ethereum === 'function') {
                this.ethereum = new Ethereum({network:config.ethereum.network})
            }

            var contract = config.ethereum.contract
            var abi = config.ethereum.abi
            var address = config.ethereum.address
            var info = config.ethereum.info
            
            if (abi && address) {
                this.contract = self.ethereum.contract(abi,address,'Inxio')
                this.abi = abi
                this.address = address
            } else if (info) {
                $.getJSON(info).then( function( data ) {
                    self.address = data.address
                    self.abi = data.abi
                    self.contract = self.ethereum.contract(self.abi,self.address,'Inxio')
                    console.log(self.contract)
                })
            } 
            /*
            if (!abi) {
                
                // retreive abi via contract.about() call + IPFS
                var tmpcontract = this.ethereum.contract(BASE_ABI,uri)
                tmpcontract.request('about').then( function(result) {
                    xio.log.debug('about ipfshash=',result)
                    self.ipfs.get(result).then( function (data) {

                        var about = JSON.parse(data)
                        xio.log.debug(about)
                        var abi = about['abi']
                        self.contract = self.ethereum.contract(abi,uri,'Inxio')
                        
                    })

                })
            } 
            this.contract = self.ethereum.contract(abi,address,'Inxio')
            */
            

            var dbname = xio.tools.md5( 'inxio-network-'+this.uri )
            this.db = xio.db(dbname)
            this.db.truncate() ////////////////////////////////////// debug


            // set routes

            this.bind(':id', this.handleResource)
            this.bind('store', function(req) {
                if (req.GET) {
                    return this.getResources('service',{'type':'service'})
                }
            })
            this.bind('store/:id', this.handleResource)
            this.bind('store/:id/offers', function(req) {
                var serviceid = req.context[':id']
                var filter = {'type': 'offer','item': serviceid}
                return this.contract.getOffers(serviceid).then(function(ids) {
                    var dl = []
                    $(ids).each(function (i,id) {
                        var d = self.getResource(id,'offer').then(function(data) {
                            //console.log(data)
                        })
                        dl.push( d )
                    })

                    return $.when.apply($,dl).then(function () {
                        return self.db.select(filter)
                    }, function(err) {
                        alert(err)
                    })

                })
            })
            this.bind('store/:id/offers/:offerid', function(req) {
                var serviceid = req.context[':id']
                var offerid = req.context[':offerid']
                
                if (req.ABOUT)
                    return self.getResource(offerid,'offer')

                if (req.PURCHASE) {

                    var offer = this.db.get(offerid)
                    var input = '0x' //req.data
                    var about = ''

                    var cost = offer.cost
                    var value = new XioValue('amount',cost,'EUR')
                    var context = {
                        'value': value
                    }
                    return self.contract.purchase(serviceid, offerid, 1, input, context)
                }
            })
            this.bind('store/:id/orders', function(req) {
                var serviceid = req.context[':id']
                var filter = {'type': 'order', 'item': serviceid}
                return this.getResources('order',filter)
            })
            this.bind('store/:id/orders/:orderid', function(req) {
                var orderid = req.context[':orderid']
                return self.getResource(orderid,'order')
            })
            this.bind('store/:id/instances', function(req) {
                var serviceid = req.context[':id']
                if (req.GET) {
                    var filter = {'type': 'resource', 'handler': serviceid}
                    return this.getResources('resource',filter)
                }
                if (req.CREATE) {
                    var input = req.data
                    var d1 = this.ipfs.put(input)
                    return $.when( d1 ).done(function ( input ) {
                        var name = toBytes('noname')
                        var about = toBytes('')
                        var input = toBytes(input)
                        var output = toBytes('')
                        return self.contract.createUserResource(name,about,serviceid,input,output)
                    })
                }

            })
           
        }


        render(req) {
            var self = this
            console.log('XioNetworkEthereumHandler>>> RENDER',req)

            if (!req.path) {
                return this.handleNetwork(req)
            }
            return super.render(req)
        }

        about(id,type) {
            return this.get(id,type).then(function(row) {
                return xio.tools.about( row )
            })
        }

        get(id,type) {
            var self = this
            return this.getResource(id,type).then(function(row) {
                return self.resolve(row)
            })

        }

        resolve(row) {

            if (!row)
                return $.Deferred().resolve(row).promise()

            console.log('====== ABOUT RESOLVE BEFORE',row)
            var self = this

            var ipfs_keys = ['about','input','output'] //,'input','output']
            var link_keys = [] //'handler','item'] //['owner','seller','buyer','worker','item','offer','handler']

            var dl = []

            for (var k in row) {
                var v = row[k]
                //console.log('RESOLVE',k,v)
                var resolve = null
                if (ipfs_keys.indexOf(k)!=-1) {
                    resolve = function(key,value) {
                        return self.ipfs.get(value).then(function(result){
                            //xio.log.debug('====== ... RESOLVE IPFS',key,value,result)
                            row[key] = result || ''
                        })
                    }
                } else if (link_keys.indexOf(k)!=-1 && v!='0') {
                    resolve = function(key,value) {
                        return self.get(value).then(function(result){
                            //xio.log.debug('====== ... RESOLVE LINK',key,value,result)
                            row[key] = result || {'id':value}
                        })
                    }
                }
                if (resolve && (typeof v === 'string' || v instanceof String)) {
                    dl.push( resolve(k,v) )
                }

            }
            
            //console.log('DL>>>',dl)
            return $.when.apply($,dl).then(function () {
                console.log('====== ABOUT RESOLVE AFTER',row)
                return row
            })
        }



        getResources(type,filter) {
            var self = this
            var typecode = this.TYPE_MAPPING_BY_NAME[type];
            console.log('getResources ...',type,filter)
            return this.contract.getResources(typecode,0).then(function(ids) {
                var dl = []
                $(ids).each(function (i,id) {
                    if (id && ! id.startsWith('0x00000')) {
                        var d = self.getResource(id,type)
                        dl.push( d )
                    }
                })

                return $.when.apply($,dl).then(function () {
                    filter = filter || {}
                    filter['type'] = type
                    return self.db.select(filter)
                }, function(err) {
                    alert(err)
                })

            })
        }


        getResource(id,type,refresh) {
            var self = this
            console.log('getResource ...',id,type)
            // quick & dirty
            var d = $.Deferred()
            var cached = this.db.get(id)
            if (cached && !refresh) {
                //xio.log.debug('... from cache',type,id)  
                //console.debug('... from cache',type,id,cached) 
                return d.resolve(cached).promise();
            }

            // quick & dirty

            if (!id || id=='0' || String(id).startsWith('0x000'))  {
                return d.resolve(null).promise();
            }

            // 
            
            return self.contract.aboutResource(id).then(function(data) {

                var typecode = data[0];
                var id = data[1];
                var owner = data[2];
                var name = data[3];
                var about = data[4];
                var status = data[5];
                var result = {
                    'id': id,
                    'type': self.TYPE_MAPPING_BY_CODE[typecode],
                    'owner': owner,
                    'status': status,
                    'name': name,
                    'about': about,
                }
                console.log(result)
                
                return result
            }).then(function(data) {
                return self.ipfs.get(data['about']).then(function(about) {
                    data['_about'] = data['about']
                    data['about'] = about
                    return data
                })
            }).then(function(data) {

                    type = type || data['type']

                    if (type=='user') {

                        return self.contract.aboutUser(id).getContent().then(function(extra) {
                            data['level'] = extra[0]
                            data['credit'] = extra[1]
                            return data
                        })
                    }
                    else if (type=='resource') {
                        return self.contract.aboutUserResource(id).then(function(extra) {
                            data['_debug'] = extra
                            data['handler'] = extra[0]
                            data['input'] = extra[1]
                            data['output'] = extra[2]
                            return data
                        })
                    }
                    else if (type=='order') {
                        /*
                        order.buyer,
                        order.orderItem.seller,
                        order.orderItem.item,
                        order.orderItem.quantity,
                        order.orderItem.input,
                        order.orderItem.provider,
                        order.orderItem.output,
                        order.orderItem.delivered
                        */
                        return self.contract.aboutOrder(id).then(function(extra) {
                            data['_debug'] = extra
                            data['buyer'] = extra[0]
                            data['seller'] = extra[1]
                            data['item'] = extra[2]
                            data['quantity'] = extra[3]
                            data['input'] = extra[4]
                            data['provider'] = extra[5]
                            data['output'] = extra[6]
                            data['delivered'] = extra[7]
                            return data
                        })
                    }
                    else if (type=='offer') {
                        return self.contract.aboutOffer(id).then(function(extra) {
                            data['_debug'] = extra
                            data['seller'] = extra[0]
                            data['item'] = extra[1]
                            data['pricing'] = extra[2]
                            data['cost'] = extra[3]
                            data['profile'] = extra[4]
                            data['ttl'] = extra[5]
                            return data
                        })
                    }                
                    else if (type=='orderitem') {
                        return self.contract.aboutOrderItem(id).then(function(extra) {
                            data['_debug'] = extra
                            data['order'] = extra[0]
                            data['item'] = extra[1]
                            data['offer'] = extra[2]
                            data['provider'] = extra[3]
                            data['input'] = extra[4]
                            data['output'] = extra[5]
                            data['quantity'] = extra[6]
                            data['shipped'] = extra[7]
                            return data
                        })
                    }
                    else if (type=='service') {
                        return self.contract.aboutService(id).then(function(extra) {
                            data['_debug'] = extra
                            data['provider'] = extra[0]
                            data['input'] = extra[1]
                            data['output'] = extra[2]
                            data['worker'] = extra[3]
                            var nboffers = extra[4]
                            data['ttl'] = extra[5]
                            return data
                        })
                    }
                    return data


            }).then(function(data) {
                console.log('****** PUT DB', id, type, data)
                self.db.put(id,data) 
                return data
            })

        }

        handleNetwork(req) {
            var self = this

            if (req.ABOUT) {

                var d1 = this.contract.about().then( function (data) {

                    var network = data[0];
                    var id = data[1];
                    var owner = data[2];
                    var typecode = data[3];
                    var status = data[4];
                    var name = data[5];
                    var about = data[6];

                    var result = {
                        'network': network,
                        'id': id,
                        'type': self.TYPE_MAPPING_BY_CODE[typecode],
                        'owner': owner,
                        'status': status,
                        'name': name,
                        'about': about,
                        'fee': data[7],
                        'rate': data[8],
                        'rate_updated': data[9]
                    }

                    return self.ipfs.get(about).then(function (about) {
                        result.about = about
                        return result
                    })
                })
                return $.when( d1 )

            }



        }


        handleResource(req) {

            var self = this

            console.log(req)

            var id = req.context[':id']
            var row = this.db.get(id)
            var type = row.type

            if (req.ABOUT) {
                return self.about(id)
            }


            if (type=='service') {



                if (req.UPDATE) {

                    var payload = req.data
                    var handler = payload.handler
                    var name = payload.name
                    var about = payload.about
                    var input = payload.input
                    var output = payload.output

                    var d1 = this.ipfs.put(about)
                    var d2 = this.ipfs.put(input)
                    return $.when( d1, d2 ).done(function ( about, input ) {
                        return service.update(name, about, handler, input, output)
                    })
                }

                if (req.CONFIGURE) {
                    var input = req.data
                    var d1 = this.ipfs.put(input)
                    return $.when( d1 ).done(function ( input ) {
                        return service.setInput(input)
                    })
                }

            }

            /*
            if (type=='order') {

                var order = this.contract.factory.order(id)

                if (req.DELIVER) {
                    var output = req.data
                    var d1 = this.ipfs.put(output)
                
                    return $.when( d1 ).done(function ( output ) {
                        return order.complete(output)
                    });
                }

                if (req.GET) {

                    var result = []
                    var dl = []
                    $(row.orderedItem).each(function(k,orderitemid){
                        dl.push( 
                            self.getResource(orderitemid,'orderitem').then(function(orderitem){
                                result.push( orderitem )
                            })
                        )
                    })
                    return $.when.apply($,dl).then(function(){ /////////// warning - then/done
                        //console.log('===>>>>>> ORDERITEMS', result)
                        return result
                    });
                }
            }
            */


        }




    } 

    window.XioNetworkEthereumHandler = XioNetworkEthereumHandler;

})();



