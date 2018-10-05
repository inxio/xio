(function(){

    XioNetwork = function(config) {

        XioApp.call(this,null,{});
        this.config = config
        if (config.ethereum) {
            var handler = new XioNetworkEthereumHandler(config)
            this.handler = xio.client(handler)
        } else if (config.server) {
            var handler = config.server
            this.handler = handler //xio.client(handler) 
        }

        //this.bind('*', this.handleNetwork)

        this.bind(':id', this.handleResource)

        this.bind('store/:id', this.handleResource)

        this.bind('store/:id', function(req) {
            var serviceid = req.context[':id']
            return this.handler.request(req.method,'store/'+serviceid,req.query)
        })
        this.bind('store/:id/offers', function(req) {
            var serviceid = req.context[':id']
            return this.handler.request(req.method,'store/'+serviceid+'/offers').then(function(resp) {
                return resp.content
            })
            /*
            // pb car GET est forwardé vers le provider
            return this.handler.request('ABOUT',serviceid).then(function(resp) {
                console.log(resp)
                return resp.content.offers
            })
            */
        })
        this.bind('store/:id/offers/:offerid', function(req) {
            var serviceid = req.context[':id']
            var offerid = req.context[':offerid']
            return this.handler.request(req.method,'store/'+serviceid+'/offers/'+offerid).then(function(resp) {
                return resp.content
            })
        })
        this.bind('store/:id/orders', function(req) {
            var serviceid = req.context[':id']
            return this.handler.request('GET','store/'+serviceid+'/orders').then(function(resp) {
                return resp.content
            })
        })
        this.bind('store/:id/orders/:orderid', function(req) {
            var serviceid = req.context[':id']
            var orderid = req.context[':orderid']
            return this.handler.request(req.method,'store/'+serviceid+'/orders/'+orderid).then(function(resp) {
                return resp.content
            })
        })
       this.bind('store/:id/instances', function(req) {
            var serviceid = req.context[':id']
            if (req.GET) {
                return this.handler.request('GET','store/'+serviceid+'/instances').then(function(resp) {
                    console.log(resp.content)
                    $(resp.content).each(function(){
                        this['@id'] = '/'+this.id
                    })
                    return resp.content
                })
            }
            if (req.CREATE) {
                return this.handler.request('CREATE','store/'+serviceid+'/instances',req.data)
            }


        })
       this.bind('store/:id/instances/:instanceid', function(req) {
            req.path = req.context[':instanceid']
            return this.handleResource(req)
        })

        this.bind('user', this.handleUser)
        this.bind('user/network', this.handleNetwork)
        this.bind('user/subscriptions', this.handleSubscriptions)
        this.bind('user/subscriptions/:id', this.handleSubscription)
        this.bind('user/purchases', this.handlePurchases)
        this.bind('user/purchases/:id', this.handleOrder)
        this.bind('user/purchases/:id/:olid', this.handleOrderItem)
        this.bind('user/sales', this.handleSales)
        this.bind('user/sales/:id', this.handleOrder)
        this.bind('user/sales/:id/:olid', this.handleOrderItem)
        this.bind('user/services', this.handleServices)
        this.bind('user/services/:id', this.handleService)
        this.bind('user/store', this.handleStore)        
        this.bind('user/store/:id', this.handleStoreItem)
        this.bind('user/users', this.handleUsers)        
        this.bind('user/users/:id', this.handleUser)
        this.bind('user/logs', this.handleLogs)     

        return this
    }
    XioNetwork.prototype.STATUS_RUNNING = 2
    XioNetwork.prototype.STATUS_PENDING = 3
    XioNetwork.prototype.STATUS_COMPLETED = 9   
    XioNetwork.prototype.PRICING_TYPE_SUBSCRIPTION = 1
    XioNetwork.prototype.PRICING_TYPE_PURCHASE = 2

    XioNetwork.prototype = Object.create(XioApp.prototype, {
        constructor: { value: XioNetwork }
    });





    XioNetwork.prototype.handleNetwork = function (req) {
        var self = this
        console.log('>>>>>>>>>>>>>>>>>>>>>>>>  handleNETWORK ')    
        console.log(req)

        /*
        if (!req.path && req.ABOUT) {
            return {
                'id': '???',
                'config': this.config
            }
        }
        */
        return this.handler.request(req.method,req.path,req.query)
        /*
        if (!req.path || req.path=='/')
            return this.handler.request(req.method,req.path,req.query)
        
        console.log('ppp',req)
        return this.handleResource(req)
        */
        
    }

    XioNetwork.prototype.handleResource = function (req) {

        var self = this
        var p = req.path.split('/')
        var resourceid = req.context[':id']

        //fix bug routing
        if (!resourceid) {
            return this.handleNetwork(req)
            //alert('ERROR missing resourceid')
        }

        console.log('>>>>>>>>>>>>>>>>>>>>>>>>  handleResource '+resourceid)    
        if (req.API) {
            alert('api')
        }
        if (req.ABOUT) {

            return this.handler.about(resourceid).then(function(resp) {

                console.log('>>>>>>>>>>>>>>>>>>>>>>>>  handleResource ABOUT STEP1', resp)  

                var about = resp.content

                if (xio.context.user)
                    var currentuser = xio.context.user.id

                if (about.owner && about.owner.id==currentuser) {
                    
                    if (about.handler && about.handler.id) {
                        about.options.push('CONFIGURE')
                        // gestion configuration     
                        if (about.handler.input)
                            var params = about.handler.input.params
                        else
                            var params = []

                        for (var i in params) {
                            var name = params[i].name
                            var value = about.input[name]
                            params[i].value = value
                        }

                        about.methods['CONFIGURE'] = {
                            'input': {
                                'params': params
                            }
                        }
                    } 
                    about.options.push('UPDATE')
                    about.methods['UPDATE'] = {
                        'input': {
                            'params': [
                                {'name': 'name', 'value': about.name },
                                {'name': 'about', 'value': JSON.stringify( about.about ) },
                                {'name': 'handler', 'value': about.handler },
                                {'name': 'input', 'value': JSON.stringify( about.input ) },
                                {'name': 'output', 'value': JSON.stringify( about.output ) },
                            ]
                        }
                    }
                }

                return about
            }).then(function(about) {
                console.log('>>>>>>>>>>>>>>>>>>>>>>>>  handleResource ABOUT STEP2', about)  
                if (about.handler) {
                    return self.handler.about(about.handler).then(function(resp) {
                        about.handler = resp.content
                        return about
                    })
                }
                return about
            }).then(function(about) {
                console.log('>>>>>>>>>>>>>>>>>>>>>>>>  handleResource ABOUT STEP3 (fix)', about)  
                about = xio.tools.about(about)
                if (about.handler) {
                    var abouthandler = xio.tools.about(about.handler)
                    about.methods = abouthandler.methods,
                    about.options = abouthandler.options
                } 
                return about
            })
        }
        if (req.CREATE) {
            var payload = req.data
            return this.handler.request('CREATE',resourceid,payload)
        }


        if (req.CONFIGURE) {
            var payload = {
                'input': req.data
            }
            return this.handler.request('CONFIGURE',resourceid,payload)
        }
        if (req.UPDATE) {
            var payload = req.data
            return this.handler.request('UPDATE',resourceid,payload)
        }
        if (req.DELETE) {
            return this.handler.delete(resourceid)
        }
        /*
        if (req.EDIT) {
            var output = req.data
            return this.updatePurchase(serviceid, output, self.STATUS_RUNNING)
        }



        if (req.DELIVER) {
            var output = req.data
            return this.updatePurchase(serviceid, output, self.STATUS_COMPLETED)
        }
        if (req.OFFER) {
            var payload = req.data
            var pricing = payload.pricing
            var cost = payload.cost
            var ttl = payload.ttl

            return this.createOffer(serviceid,pricing,cost,ttl).then(function(resp) {
                return resp;
            })
        }
        if (req.LOGS) {
            return this.getServiceLog(serviceid).then(function(resp) {
                return resp
            })
        }
        */
        return this.handler.request(req.method,resourceid,req.data) // +'/'+req.path

    }

    XioNetwork.prototype.handleSubscriptions = function (req) {

        if (req.ABOUT) {

            about = {
                'name': 'subscriptions'
            }
            about.methods = {}

            return xio.tools.about(about)
        }
        if (req.GET) {
            return this.handler.get('user/subscriptions') 
            /*
            return this.handler.select(function(row) {
                return (
                    row.type=='service' && row.expire>0
                )
            })
            */
        }
    }
    XioNetwork.prototype.handleSubscription = function (req) {

        var serviceid = req.context[':id']

        if (req.ABOUT) {

            console.log('??handleSubscription',req)
            return this.handler.about(serviceid).then(function(resp) {

                var about = resp.content

                if (about.input)
                    var params = about.input.params 
                else 
                    var params = []

                params.push({'name': '_name'})

                about.options.push('CREATE')
                about.methods['CREATE'] = {
                    'input': {
                        'params': params
                    }
                }

                return about

            })
        }

        if (req.CREATE) {
            var data = req.data
            var name = data._name || 'new instance'
            delete data._name
            var payload = {
                'name': name,
                'handler': serviceid,
                'input': data,
            }
            return this.handler.request('CREATE','user/services',payload)
        }


    }


    XioNetwork.prototype.handlePurchases = function (req) {

        if (req.ABOUT) {
            return {'name': 'purchases'}
        }
        if (req.GET) {
            return this.handler.get('user/purchases')
        }

    }
    XioNetwork.prototype.handleSales = function (req) {

        if (req.ABOUT) {
            return {'name': 'sales'}
        }
        if (req.GET) {
            return this.handler.get('user/sales')
        }

    }
    XioNetwork.prototype.handleUsers = function (req) {

        if (req.ABOUT) {
            return {'name': 'users'}
        }
        if (req.GET) {
            return this.handler.get('user/users')
        }

    }
    XioNetwork.prototype.handleLogs = function (req) {

        if (req.ABOUT) {
            return {'name': 'logs'}
        }
        if (req.GET) {
            return this.handler.get('user/logs')
        }

    }

    XioNetwork.prototype.handleStore = function (req) {
        var self = this
        if (req.ABOUT) {
            return {'name': 'store'}
        }
        if (req.GET) {

            return this.handler.request('GET','user/store')

            var query = {
                'filter': {
                    'type': 'offer'
                }
            }
            return this.handler.request('GET','user/store',query).then(function(resp) {
                var offers = resp.content
                var result = []
                var data = {}
                $(offers).each(function(k,offer) {
                       
                    //console.log(offer)
                    if (offer.item && offer.item.id) {
                        var productid = offer.item.id
                        if (!data[productid]) {
                            data[productid] = true
                            //data[productid].offers = [offer]
                            result.push(offer.item)
                        } 
                        else {
                            //data[productid].offers.push(offer)     
                        }              
                    }

                })
                return result
            })
            
        }
    }
    XioNetwork.prototype.handleStoreItem = function (req) {
        var self = this
        var productid = req.context[':id']

        if (req.ABOUT) {
            return self.handler.about(productid)
        }

        if (req.SUBSCRIBE || req.PURCHASE) {
            return this.handler.request('PURCHASE', productid, req.data)
        }

    }
    XioNetwork.prototype.handleUser = function (req) {
        var self = this
        if (req.ABOUT) {

            return this.handler.about('user').then(function(resp){    
                var about = resp.content
                var registered = about.name    
                
                about['options'] = []
                about['methods'] = {}
                if (!registered) {
                    about['options'].push('REGISTER')
                    about['methods']['REGISTER'] = {
                        'input': {
                            'params': [
                                {'name':'name','required':true},
                                {'name':'url'}
                            ]
                        }
                    }   
                } else {
                    about['options'].push('UPDATE')
                    about['methods']['UPDATE'] = {
                        'input': {
                            'params': [
                                {'name':'name','required':true,'value':about['name']},
                                {'name':'url','value':about.about['url']},
                                {'name':'logo','value':about.about['logo']},
                                {'name':'description','value':about.about['description']}
                            ]
                        }
                    }  
                }

                about['options'].push('SEND')
                about['methods']['SEND'] = {
                    'input': {
                        'params': [
                            {'name':'id','required':true},
                            {'name':'amount'}
                        ]
                    }
                }   
                
                about['resources'] = {
                    'services': {},
                    'subscriptions': {},
                    'purchases': {},
                    'sales': {},
                    'transactions': {},
                    'logs': {}
                }
                about['ui'] = {
                    'class': 'html',
                    'view': 'row'
                }
                return about
            })
        }
        if (req.REGISTER) {
            /*
            var payload = req.data
            var name = payload['name']
            delete payload['name']
            return this.handler.createUser(name,payload)
            */
            var data = req.data
            var name = data['name']
            delete data['name']

            var payload = {
                'name': name,
                'about': data
            }
            return this.handler.request('REGISTER','user',payload)
        }
        if (req.UPDATE) {
            /*
            var payload = req.data
            var name = payload['name']
            delete payload['name']
            return this.handler.updateUser(name,payload)
            */
            var data = req.data
            var name = data['name']
            delete data['name']

            var payload = {
                'name': name,
                'about': data
            }
            return this.handler.request('UPDATE','user',payload)
        }
        if (req.SEND) {
            /*
            var userid = data['id']
            var value = data['value']
            return this.send(userid,value)
            */
        }

    }
    XioNetwork.prototype.resolve = function (resp) {
        var data = resp.content
        if (!data || !data instanceof Object)
            return resp

        console.log('====== ABOUT RESOLVE BEFORE',data)
        var self = this

        var ipfs_keys = ['about','input','output']
        var link_keys = ['handler','item','owner','seller','buyer','worker']

        var dl = []

        for (var k in data) {
            var v = data[k]
            //console.log('RESOLVE',k,v)
            var resolve = null
            if (ipfs_keys.indexOf(k)!=-1) {
                resolve = function(key,value) {
                    return self.handler.ipfs.get(value).then(function(result){
                        //xio.log.debug('====== ... RESOLVE IPFS',key,value,result)
                        data[key] = result || ''
                    })
                }
            } else if (link_keys.indexOf(k)!=-1 && v!='0') {
                resolve = function(key,value) {
                    return self.handler.get(value).then(function(r){
                        if (r.content) {
                            //xio.log.debug('====== ... RESOLVE LINK',key,value,result)
                            data[key] = r.content || {'id':value}
                        }
                    })
                }
            }
            if (resolve && (typeof v === 'string' || v instanceof String)) {
                dl.push( resolve(k,v) )
            }

        }
        
        //console.log('DL>>>',dl)
        return $.when.apply($,dl).then(function () {
            console.log('====== ABOUT RESOLVE AFTER',data)
            resp.content = data
            return resp
        })
    } 

    XioNetwork.prototype.handleOrder = function (req) { 
        var self = this
        var orderid = req.context[':id']

        if (req.ABOUT) {

            return this.handler.about(orderid).then(self.resolve).then(function(resp) {
                var about = resp.content
                //var input = about.item.input
                console.log(about)
                if (about.status==0) {
                    about['options'].push('DELIVER')
                    about['methods']['DELIVER'] = {
                        //'input': input
                    }
                }
                return about
            })
        }

        if (req.DELIVER) {

            var payload = {
                'output': req.data,
            }
            return this.handler.request('DELIVER',orderid,payload)
        }


        if (req.GET) {
            return this.handler.get(orderid)
        }
    }

    XioNetwork.prototype.handleOrderItem = function (req) { 
        var self = this
        var orderid = req.context[':id']
        var orderitemid = req.context[':olid']

        if (req.ABOUT) {

            return this.handler.about(orderitemid).then(self.resolve).then(function(resp) {
                var about = resp.content
                if (about.status==0) {
                    about['options'].push('DELIVER')
                    about['methods']['DELIVER'] = {
                        //'input': input
                    }
                }
                return about
            })
        }

        if (req.DELIVER) {
            var payload = {
                'output': req.data,
            }
            return this.handler.request('DELIVER',orderid,payload)
        }

        if (req.GET) {
            return this.handler.get(orderitemid)
        }
    }


})();

/*

    return this.handler.get(orderid).then(function(about) {
        var seller = about.seller
        var buyer = about.buyer || {}
        var offer = about.offer
        var item = about.item
        var ammountpaid = offer.cost
        /*
        if (offer.pricing==1) {
            ordertype = 'purchase'
        } else if (offer.pricing==2) { 
            ordertype = 'subscription'
        } else {
            ordertype = '?? '+offerid+' '+offer.pricing
        }

        ordertype = offer.pricing

        //var valueEUR = new XioValue('amount',ammountpaid,'WEI').convert('EUR')


        var order = {
            '@type': 'InxioOrder',
            'identifier': about.id,
            'seller': seller,
            'customer': buyer,
            //'billingAddress': a,
            'orderedItem': {
                '@id': about.item.id,
                '@context': 'Product',
                'name': about.item.name
            },
            //'orderDate': date.label,
            'orderNumber': about.id, //row.transactionHash,
            'orderStatus': 'complete',
            'paymentMethod': 'ethereum',
            'paymentMethodId': 'xrn:ethereum:$idnetwork',
            'paymentStatus': 'complete',
            'partOfInvoice': {
                '@id': '??',
                '@context': 'Invoice',
                'accountId': buyer.id,
                //'confirmationNumber': row.transactionHash,
                'totalPaymentDue': {
                    '@type': "PriceSpecification",
                    //'price': ammountpaid,
                    //'priceCurrency': "WEI"
                },
            },
            'acceptedOffer': {
                '@id': offer.id,
                'price': offer.cost,
                'priceCurrency': 'EUR'
            },
            'about': {
                'type': ordertype,
                //'paid': valueEUR.label,
                //'fee1': fee1EUR.label,
                //'fee2': fee2EUR.label,
                //'event': row
            },
        }

        //order.about['transaction'] = tx
        //order.about['block'] = block

        return order


    return this.contract.events.get('logOrder').then(function(data) {
        var result = []
        var txs = []
        $.each( data, function(k,row) {
            if (row.returnValues.userid==userid) {

                var d = self.ethereum.web3.eth.getTransaction(row.transactionHash).then( function(tx) {

                    return self.ethereum.web3.eth.getBlock(tx.blockNumber).then( function(block) { 

                        var accountid = row.returnValues.userid
                        var serviceid = row.returnValues.serviceid
                        var service = self.handler.get(serviceid)
                        var offerid = row.returnValues.offerid
                        var orderid = row.returnValues.orderid
                        var offer = self.handler.get(offerid)
                        var seller = service.owner
                        var fee = row.returnValues.fee
                        var ammountpaid = row.returnValues.value
                        if (offer.pricing==1) {
                            ordertype = 'purchase'
                        } else if (offer.pricing==2) { 
                            ordertype = 'subscription'
                        } else {
                            ordertype = '?? '+offerid+' '+offer.pricing
                        }

                        // ihm price
                        var valueEUR = new XioValue('amount',ammountpaid,'WEI').convert('EUR')
                        var fee1EUR = new XioValue('amount',fee,'WEI').convert('EUR')
                        var fee2EUR = new XioValue('amount',tx.gas,'WEI').convert('EUR')
                        var date = new XioValue('datetime',block.timestamp,'TIMESTAMP').convert('ISO')
                        
                        
                        // convert contrract log to schema Order : http://schema.org/Order
                        var order = {
                            'identifier': orderid,
                            'seller': seller,
                            'billingAddress': accountid,
                            'orderedItem': {
                                '@id': serviceid,
                                '@context': 'Product',
                                'name': service.name
                            },
                            'orderDate': date.label,
                            'orderNumber': row.transactionHash,
                            'orderStatus': 'complete',
                            'paymentMethod': 'ethereum',
                            'paymentMethodId': 'xrn:ethereum:$idnetwork',
                            'paymentStatus': 'complete',
                            'partOfInvoice': {
                                '@id': serviceid,
                                '@context': 'Invoice',
                                'accountId': accountid,
                                'confirmationNumber': row.transactionHash,
                                'totalPaymentDue': {
                                    '@type': "PriceSpecification",
                                    'price': ammountpaid,
                                    'priceCurrency': "WEI"
                                },
                            },
                            'acceptedOffer': {
                                '@id': offerid,
                                'price': service.cost,
                                'priceCurrency': 'EUR'
                            },
                            'about': {
                                'type': ordertype,
                                'paid': valueEUR.label,
                                'fee1': fee1EUR.label,
                                'fee2': fee2EUR.label,
                                'event': row
                            },
                        }


                        order.about['transaction'] = tx
                        order.about['block'] = block

                        return order
                    })
                })

                result.push(d)
                //txs.push()
            }
        })

        // add tx
        return $.when.apply($, result).then( function() {
            
            return {
                'content': $.makeArray(arguments).sort()
            }
        });


    })


})
*/

