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

	Contract = function(ethereum,address,abi) {

        console.log('init Contract '+address)
        this.ethereum = ethereum;
        this.address = address
        this.abi = abi;
        this.api = {}
        for (var i in this.abi) {
            var info = this.abi[i]
            if (info.type=='function') {
                this.api[info.name] = info
            }
        }
        console.log(this.api)
        if (this.ethereum.v1) {
            this.instance = new this.ethereum.web3.eth.Contract(this.abi,this.address); ///// v1.x
        } else {
            this.instance = this.ethereum.web3.eth.contract(this.abi).at(this.address); //// v0.x
        }

        
        console.log(this.instance)
        var self = this
        this.events = {
            get: function(topic,params) {
                params = {fromBlock: 0, toBlock: 'latest'}
                var events = self.instance.allEvents(params)
                //return async(events.get)()

                return async( function(callback) {
                    events.get(callback)
                })()
            }
        }
    };
	Contract.prototype = {

        getTransactions: function() {
            var filter=this.ethereum.web3.eth.filter({fromBlock: 0, toBlock: 'latest', address: this.address});

            var d = $.Deferred();
            console.log('======transactions',filter)  
            filter.get(function(error, result) {
                if (error) {
                    console.log('====RESPONSE FAILED',error)
                    d.reject(error);
                } else {
                    console.log('====RESPONSE SUCCEED',result)
                    d.resolve(result);
                }
            });
            return d.promise()
            //return this._transactions
        },
        estimate: function(method,params,callback) {
            params['_estimate'] = true
            return this.request(method,params).then(function(data) {
                console.log('estimate ...',data)
            })
        },
        request: function(method,kwargs,context) {

            params = kwargs || {}
            console.log('call Contract '+this.address)

            var info = this.api[method]

            // arguments
            var args = []
            for (var i in info.inputs) {
                var input = info.inputs[i]
                args.push( kwargs[input.name] )    
            }
            // context
            /*
            var context = {}
            var account = params['_from'] || this.eth.account;
            context['from'] = account

            var value = params['_value']
            if (value) {
                value = this.eth.web3.toWei(0.00000000000000005, "ether")
            }

            if (info.payable) {
                value = this.eth.web3.toWei(value, "Finney")   
                context['value'] = value
            }
            if (params['_gas']) {
                context['gas'] = params['_gas']
            }
            */
            console.log('====REQUEST',method,args,context)
            console.log(this.api[method])


            if (this.ethereum.v1) {
                return this.requestv1(method,args,context)
            } else {
                return this.requestv0(method,args,context)          
            }    
        },

        requestv1: function(method,args,context) {
            // en direct sans metamask ?   
            var web3 = this.ethereum.web3 
            //args[0] = web3.utils.toHex(args[0])

            var istransaction = !this.api[method].constant
            var method = this.instance.methods[method]
            var methodhandler = method.apply(null,args)

            if (istransaction) {
                var handler = methodhandler.send
            } else {
                var handler = methodhandler.call
            }

            return handler(context)
        },

        requestv0: function(method,args,context) {

            var istransaction = !this.api[method].constant

            args.push(context)

            var d = $.Deferred();
            args.push(function(error,result) {
                if (error) {
                    console.log('====RESPONSE FAILED',error)
                    d.reject(error);
                } else {
                    console.log('====RESPONSE SUCCEED',result)
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

	Ethereum = function(web3) {

        console.log('init Ethereum ',web3)

        // comment detecter quel type de web3 ? metamask ou celui de ext

        if (typeof web3 !== 'undefined') { 
            // Use Mist/MetaMask's provider
            console.log('======= METAMASK WEB3')
            var web3 = web3 //new Web3(web3.currentProvider);
        } else {
            console.log('======= XIO WEB3')
            var web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
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
                  console.log('This is mainnet')
                  break
                case "2":
                  console.log('This is the deprecated Morden test network.')
                  break
                case "3":
                  console.log('This is the ropsten teest network.')
                  break
                default:
                  console.log('This is an unknown network.')
            }
            console.log('Ethereum web3 version '+this.web3.version+' '+this.v1)
            console.log('Ethereum network '+netId)
            console.log('Ethereum account '+this.account)

        })

        this.web3.eth.getBlockNumber( function(e,r) { 
            console.log('Ethereum blockNumber '+r)
            self.blockNumber = r;
        })
       
		return this;
	};


	Ethereum.prototype = {

        getBalance: function(address) {
            return async( this.web3.eth.getBalance )( address )
        },
        registerContract: function(name,abi,addresses) {
            console.log('register contract '+name+' '+addresses)
            this.contracts[name] = new Contract(this,addresses,abi)
            console.log(this.contracts)
            return this.contracts[name]
        },
        contract: function(abi,addresses) {
            var contract = new Contract(this,addresses,abi)
            return contract
        }
    
    }

})();


