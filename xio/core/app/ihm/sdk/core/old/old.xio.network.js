(function(){

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

    XioNetwork = function(uri) {

        if (uri.startsWith('0x')) {
            // ethereum based network
            if (typeof Ethereum === 'function') {
                this.ethereum = new Ethereum()
            }
            var tmpcontract = this.ethereum.contract(abi,address)

        }

        var self = this
        $.getJSON( 'sdk/ext/xio/contracts/xio/latest/xio.json', function( data ) { 
            var netid = 'test'
            var address = data['addresses'][netid]
            var abi = data['abi']['Xio']
            self.contract = self.ethereum.registerContract('xio',abi,address)

            // load cache data
            self.data = {}
            self.getServices().then( function(data) {
                self.data.store = data
            })
            xio.context.user.getServices().then( function(data) {
                self.data.services = data
            })
        })          

    }
    XioNetwork.prototype.getBalance = function(address) {
        return this.ethereum.web3.eth.getBalance(address)
    };
    XioNetwork.prototype.getUserFromKey = function(key) {
        return new XioUser(this,key)
    };
    XioNetwork.prototype.amount = function(value,currency_from,currency_to) {
        currency_from = currency_from || 'wei'
        currency_to = currency_to || 'euro'
        return new DxioAmount(value,currency_from).convert(currency_to)
    };
    XioNetwork.prototype.getServices = function() {
        return this.contract.request('getServices').then( function(data) {
            console.log(data)
            var result = []
            for (var i in data) {
                result.push({
                    'id': data[i]
                })
            }
            return result
        })
    };


})();



