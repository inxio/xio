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

        if (typeof Ethereum === 'function') {
            this.ethereum = new Ethereum()
        }
        if (typeof Ipfs === 'function') {
            this.ipfs = new Ipfs()
        }

        if (uri && uri.startsWith('0x')) {
            // ethereum based network
            var self = this
            var tmpcontract = this.ethereum.contract(BASE_ABI,uri)
            tmpcontract.request('about').then( function(result) {
                console.log('about ipfshash=',result)
                self.ipfs.get(result).then( function (data) {

                    var about = JSON.parse(data)
                    console.log(about)
                    var abi = about['abi']
                    self.contract = self.ethereum.contract(abi,uri)
                    console.log(this.contract)
                })

            })

            /*
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
            */

        }

        

    }
    


})();



