/*


    // https://github.com/ethereum/wiki/wiki/JavaScript-API#a-note-on-big-numbers-in-web3js


Error: the tx doesn't have the correct nonce. account has nonce of: 14 tx has nonce of: 0
-> deconnecter metamask et le reconnecter


diff web3

web3 <1.0
- eth.version.netId
- eth.contract

web3 1.0
- eth.net.getId ?
- eth.Contract ?

*/

(function(){


    function async( func ) {
        return function() {
            var self = this
            var d = $.Deferred();
            var callback = function(error, result){ 
                if (error) {
                    d.reject(error);
                } else {
                    d.resolve(result);
                }
            }
            var args = arguments;
            args[args.length] = callback;
            args.length++;
            func.apply(self, args);
            return d.promise()
        }
    }

    function methodWrapper(contract,name) {
        return function() {
            //alert('call '+name)
            var args = Array.prototype.slice.call(arguments);
            var lastarg = args.slice(-1)[0];
            if (typeof lastarg === "object")
                context = args.pop()
            else
                context = {}
            return contract.request(name,args,context)
        }
    }

    function instanceFactory(ethereum,abis,cls) {
        return function(address) {
            var contract = new Contract(ethereum,address,abis,cls)
            return contract
        }
    }

	Contract = function(ethereum,address,abi,cls) {

        xio.log.debug('init Contract '+address)
        var self = this

        this.ethereum = ethereum;
        this.address = address

        if (abi instanceof Array) {
            this.abi = abi;
            this.abis = {}
        } else if (abi instanceof Object) {
            this.abis = abi
            this.abi = this.abis[cls];
        }
        
        // method wrapper
        this.api = {}
        if (this.abi) {
            for (var i in this.abi) {
                var info = this.abi[i]
                if (info.type=='function') {
                    this.api[info.name] = info
                    this[info.name] = methodWrapper(this,info.name)
                }
            }
        }

        // instance wrapper
        this.factory = {}
        if (this.abis) {
            for (var cls in this.abis) {
                this.factory[cls.toLowerCase()] = instanceFactory(ethereum,this.abis,cls)
            }
        }

        // create instance
        if (this.address) {
            if (this.ethereum.v1) {
                this.instance = new this.ethereum.web3.eth.Contract(this.abi,this.address); ///// v1.x
            } else {
                this.instance = this.ethereum.web3.eth.contract(this.abi).at(this.address); //// v0.x
            }
        }
        console.log(this)


        /*
        // require infura WS support .. comming soon

        this.instance.events.allEvents(function(obj) {
            xio.log.debug(obj)
            //alert('contract event')
        })

        this.instance.events.allEvents({ fromBlock: 'latest' })
            .on('data', xio.log.debug)
            .on('changed', xio.log.debug)
            .on('error', xio.log.debug)


        */



        // event handling
        this.eventblock = 0
        this.eventsubscribers = {}

        this.events = {

            on: function(topic,callback) {

                if (!self.eventsubscribers[topic])
                    self.eventsubscribers[topic] = []
                self.eventsubscribers[topic].push(callback)
            },

            get: function(topic) {
                topic = topic || 'allEvents'
                params = {fromBlock: 0, toBlock: 'latest'}
                return self.instance.getPastEvents(topic,params,function(e,events) {
                    return events
                })
            }
        }

        xio.schedule('ethereum',10,function() {
            console.log('... ethereum event listener')
            if ( $.isEmptyObject(self.eventsubscribers) )
                return
            console.log('check events', self.eventblock, self.eventsubscribers)
            var params = {fromBlock: self.eventblock+1, toBlock: 'latest'}
            self.instance.getPastEvents('allEvents',params,function(e,events) {
                $.each(events, function(k,event) {
                    xio.log.debug(event)
                    self.eventblock = event.blockNumber
                    var topic = event.event
                    $.each( self.eventsubscribers[topic], function(k2,callback) {
                        callback(event)
                    }) 
                })       
            })
        })

        return this

    };
	Contract.prototype = {

        getBalance: function() {
            return this.ethereum.web3.eth.getBalance(this.address)
        },

        getTransactions: function() {
            var filter = {fromBlock: 0, toBlock: 'latest', address: this.address}
            return this.ethereum.web3.eth.getPastLogs(filter)
        },
        estimate: function(method,params,callback) {
            params['_estimate'] = true
            return this.request(method,params).then(function(data) {
                xio.log.debug('estimate ...',data)
            })
        },
        request: function(method,args,context) {

            
            xio.log.debug('call Contract '+this.address)
            console.log('==== CONTRACT REQUEST',method,args,context)

            var info = this.api[method]

            // arguments
            /*
            var args = []
            for (var i in info.inputs) {
                var input = info.inputs[i]
                args.push( kwargs[input.name] )    
            }
            */

            // context
            //if (!context.from)
            //    context.from = xio.context.user.account.account('ethereum').address

            //if (context.value)
            //    value = this.eth.web3.toWei(0.00000000000000005, "ether")
            //}


            //if (params['_gas']) {
            //    context['gas'] = params['_gas']
            //}

            
            xio.log.debug(this.api[method])

            try {
                if (this.ethereum.v1) {
                    return this.requestv1(method,args,context)
                } else {
                    return this.requestv0(method,args,context)          
                } 
            } catch(e) {
                console.log(e)
                alert('ERROR'+e)
            }
   
        },

        requestv1: function(method,args,context) {
            var self = this

            var web3 = this.ethereum.web3 
            //args[0] = web3.utils.toHex(args[0])

            
            //xio.log.debug(handler)

            // auto convert ascii to bytes 
            var abi = this.api[method]
            var inputs = this.api[method].inputs;
            var args_fixed = []
            for (var i in inputs) {
                var value = args[i]
                /*
                if (inputs[i].type.startsWith('bytes') ) {
                    console.log('fix input',inputs[i],value)
                    value = web3.utils.fromAscii(value)
                    console.log('fixed input =>',value)
                }
                */
                args_fixed.push(value)
            }
            args = args_fixed


            var istransaction = !this.api[method].constant && !this.api[method].view
            var method = this.instance.methods[method]
            var methodhandler = method.apply(null,args)
            if (!context.account) {
                try {
                    context.account = xio.context.user.account.account('ethereum')
                } catch(e) {
                    if (this.ethereum.account)
                        context.account = this.ethereum.account
                }
            } 
            account = context.account



            if (istransaction) {
                // http://web3js.readthedocs.io/en/1.0/web3-eth-accounts.html#eth-accounts

                var key = account.private //account.unlock()

                var gasmax = 5000000 

                var value = context.value || new XioValue('amount',0,'wei')
                if (value && value.label) {
                    //value = web3.toWei(value, "Finney")
                    //if value = new XioValue('amount',balance,'wei')
                }

                var valueWEI = Math.ceil( value.convert('WEI').value )
                var value = valueWEI || 0
                
                var data = methodhandler.encodeABI()

                var params = {
                    from: account.address,
                    to: self.address,
                    value: value,
                    data: data
                }

                console.log('transaction',method,args)
                console.log('transaction',params)

                var estimateparams = {
                    from: account.address,
                    value: value,
                    data: data,
                    gas: gasmax
                }
                return methodhandler.estimateGas(estimateparams).then( function(gasAmount) {
                    if (gasAmount==gasmax) {
                        alert('out of gas '+gasmax+' '+gasAmount)
                        return
                    }
                    xio.log.debug('>>>>>>> GAS AMOUNT ',gasAmount)
                    params['gas'] = gasAmount*2 // tofix pb recurent de out of gas
                    var confirm = {
                        'title': 'Transaction',
                        'description': 'Confirm transaction : '+value.label+' ... '+valueWEI+' wei'
                    }

                    // tofix : replace app.confirm by xio.ui.confirm
                    
                    return app.confirm(confirm).then(function(){

                        console.log('>>>>>>> SEND RAW TRANSACTION ',method,args,context,params)
                        
                        return web3.eth.accounts.signTransaction(params, key).then( function(signed) {
                            return web3.eth.sendSignedTransaction(signed.rawTransaction).then( function(tx,err) {
                                console.log('TX=',tx,err)
                                xio.log.debug( tx )
                                return tx
                                // tx receipt deja ok donc minage done
                                /*
                                var d = $.Deferred();
                                var waitResult = function() { 
                                    xio.log.debug( '... check tx', tx.transactionHash)
                                    web3.eth.getTransactionReceipt(tx.transactionHash, function(error, receipt) {
                                        xio.log.debug( error,receipt )
                                        if (error) {
                                            d.reject(error);
                                        } else if (receipt == null) {
                                            alert('null')
                                            setTimeout(waitResult, 100);
                                        } else {
                                            alert('ok')
                                            d.resolve(receipt);
                                        }
                                    });

                                }
                                waitResult()
                                return d.promise()
                                */
                            }, function(err) {alert(err)})
                        })
                    })
                },function(err) {alert(err)})


                return handler(context)
            } else {

                var handler = methodhandler.call
                context = {
                    from: account.address
                }
                return handler(context).then(function(result) {
                    //console.log('=============== RESULT',result)
                    //console.log('=============== RESULT ABI',abi)
                    // auto fix
                    if (abi.constant) {
                        for (var i in abi.outputs) {

                            /*
                            if (result[i] && abi.outputs[i].type.startsWith('bytes')) {
                                var vin = result[i]
                                var vout = web3.utils.toAscii(vin).replace(/\u0000/g, '')
                                result[i] = vout
                                console.log('fix output',abi.outputs[i],vin,vout)
                            }
                            */
                           

                        }
                    }
                    return result;
                })
            }

            
        },

        requestv0: function(method,args,context) {

            var istransaction = !this.api[method].constant

            args.push(context)

            var d = $.Deferred();
            args.push(function(error,result) {
                if (error) {
                    xio.log.debug('====RESPONSE FAILED',error)
                    d.reject(error);
                } else {
                    xio.log.debug('====RESPONSE SUCCEED',result)
                    d.resolve(result);
                }
            })

            if (!istransaction) {
                var handler = this.instance[method].call
            } else {
                var handler = this.instance[method].sendTransaction
            }
            handler.apply(null,args)
            return d.promise()
        },
    }




	Ethereum = function(config) {

        config = config || {}

        if (config.network=='ropsten') {
            this.endpoint = 'https://ropsten.infura.io'
        } else if (config.network=='mainnet') {
            this.endpoint = 'https://mainnet.infura.io'
        } else if (config.network=='testrpc') {
            this.endpoint = 'http://localhost:8545'
        } else if (config.network) {
            this.endpoint = config.network
        }   

        web3 = undefined

        //xio.log.debug('init Ethereum ',web3)

        // comment detecter quel type de web3 ? metamask ou celui de ext

        if (typeof web3 !== 'undefined') { 
            // Use Mist/MetaMask's provider
            xio.log.debug('======= METAMASK WEB3')
            var web3 = web3 //new Web3(web3.currentProvider);
        } else {
            xio.log.debug('======= XIO WEB3')
            var web3 = new Web3(
                new Web3.providers.HttpProvider(this.endpoint)
            );
        }

        this.web3 = web3;

        this.v1 = (this.web3.version.startsWith('1.'))

        this.account = web3.eth.defaultAccount;
        this.netId = null;
        this.contracts = {};
        var self = this

        // pb get version sur web3 v1
        //web3.eth.net.getNetworkType([callback])
        if (this.v1)
            h = this.web3.eth.net.getId
        else
            h = this.web3.version.getNetwork

        h((err, netId) => {

            this.netId = netId

            switch (netId) {
                case "1":
                  xio.log.debug('This is mainnet')
                  break
                case "2":
                  xio.log.debug('This is the deprecated Morden test network.')
                  break
                case "3":
                  xio.log.debug('This is the ropsten teest network.')
                  break
                default:
                  xio.log.debug('This is an unknown network.')
            }

            xio.log.info('Ethereum web3 version '+this.web3.version+' '+this.v1)
            xio.log.info('Ethereum endpoint '+this.endpoint)
            xio.log.info('Ethereum network '+netId)
            xio.log.info('Ethereum account '+this.account)

        })

        this.web3.eth.getBlockNumber( function(e,r) { 
            xio.log.info('Ethereum blockNumber '+r)
            self.blockNumber = r;
        })
        xio.log.info('Ethereum ready')
		return this;
	};


	Ethereum.prototype = {

        send: function(address,amount) {

            var self = this

            var account = xio.context.user.account.account('ethereum')
            var key = account.private //account.unlock()

            var params = {
                'from': account.address,
                'to': address,
                'value': amount,
                'data': ''
            }

            console.log(params)
            console.log(key)

            var gasmax = 5000000 

            return this.web3.eth.estimateGas({gas: gasmax}).then( function(gasAmount) {

                if (gasAmount==gasmax) {
                    alert('out of gas')
                    return
                }
                xio.log.debug('>>>>>>> GAS AMOUNT ',gasAmount)
                params['gas'] = gasAmount

                var confirm = {
                    'title': 'Transaction',
                    'description': 'Send amount to user '+address,
                    'amount': amount,
                    'fee': gasAmount,
                }
                console.log(confirm)
                return app.confirm(confirm).then(function(){
                    return self.web3.eth.accounts.signTransaction(params, key).then( function(signed) {
                        return self.web3.eth.sendSignedTransaction(signed.rawTransaction).then( function(tx) {
                            xio.log.debug( tx )
                            return tx

                        })
                    })
                }).catch(function(err) {
                    alert('error '+err)
                })
            })
        },

        getBalance: function(address) {
            return async( this.web3.eth.getBalance )( address )
        },

        getTransactions: function(address) {
            alert('not implemented')
            var filter = {
                fromBlock: 0, 
                toBlock: 'latest', 
                address: address,
                topics: [null]
            }
            return this.web3.eth.getPastLogs(filter)
        },

        registerContract: function(name,abi,addresses) {
            xio.log.debug('register contract '+name+' '+addresses)
            this.contracts[name] = new Contract(this,addresses,abi)
            xio.log.debug(this.contracts)
            return this.contracts[name]
        },
        contract: function(abi,addresses,cls) {
            var contract = new Contract(this,addresses,abi,cls)
            return contract
        }
    
    }

})();


