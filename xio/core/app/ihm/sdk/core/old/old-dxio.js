(function(){

    DxioUserContract = function(dapp,user) {
        this.dapp = dapp
        this.web3 = this.dapp.ethereum.web3
        this.user = user
        this.contract = this.dapp.contract // pb car pas encore chargé
        return this 
    }
    DxioUserContract.prototype.request = function(method) {
        this.contract = this.dapp.contract
        var args = Array.from(arguments).slice(1);
        if (!this.contract.api[method])
            alert(method+' not found in contract ABI')
        var istransaction = (!this.contract.api[method].constant)
        var method = this.contract.instance.methods[method]
        var methodhandler = method.apply(null,args)
        var data = methodhandler.encodeABI()
        console.log(methodhandler)

        if (!istransaction) {
            var handler = methodhandler.call
            return methodhandler.call({
                from: this.user.address
            })
        }
        var params = {
            from: this.user.address,
            to: this.contract.address,
            gas: 2000000,
            chainId: 1, 
            data: data
        }
        console.log('....params: ',params)
        var self = this
        return this.web3.eth.accounts.signTransaction(params, this.user.key).then( function(signed) {
            return self.web3.eth.sendSignedTransaction(signed.rawTransaction).then( console.log )
        })
    }




    DxioUser = function(dapp,key) {
        this.dapp = dapp
        this.web3 = this.dapp.ethereum.web3
        this.contract = new DxioUserContract(this.dapp,this)
        this.account = null
        this.id = 0
        this.level = 0
        this.balance = 0
        if (key) {
            this.account = this.web3.eth.accounts.privateKeyToAccount(key)
            this.address = this.account.address
            this.key = this.account.privateKey
        } else {
            this.loadSession()
        }
        this.dapp._token = this.token
        return this
    }
    DxioUser.prototype.loadSession = function() {
        session = JSON.parse( localStorage.getItem('xio.user.session') || '{}')
        this.name = session.name
        this.id = session.id
        this.token = session.token
        this.address = session.address
        this.level = session.level
        document.cookie = "token="+this.token+";path=/";
        var self = this
        if (this.address) {
            this.hname = this.web3.utils.sha3(this.name)
            this.web3.eth.getBalance(this.address).then( function(balance) {
                self.balance = self.dapp.amount(balance)
            }) 
        }

    }
    DxioUser.prototype.saveSession = function() {
        localStorage.setItem('xio.user.session',JSON.stringify({
            'id': this.id,
            'name': this.name,
            'address': this.address,
            'token': this.token,
            'level': this.level
        }))
    }
    DxioUser.prototype.clearSession = function() {
        this.id = null
        this.name = null
        this.token = null
        this.address = null
        this.account = null
        localStorage.removeItem('xio.user.session')
        document.cookie.split(";").forEach(function(c) { document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); });
    }
    DxioUser.prototype.importKey = function(keyname,keycontent) {
        if (keyname.startsWith('xio.user.') && keycontent) {
            alert('import',keyname)
            localStorage.setItem(keyname,keycontent);
        } else {
            alert('error',keyname)
        }
    }
    DxioUser.prototype.exportKey = function() {
        var hash = this.web3.utils.sha3(this.name)
        var keyname = 'xio.user.'+hash
        var keycontent = localStorage.getItem(keyname)
        
        var blob = new Blob(['test'], {type: 'octet/stream'});
        if(window.navigator.msSaveOrOpenBlob) {
            window.navigator.msSaveBlob(blob, keyname);
        } else{
            
            var elem = window.document.createElement('a');
            elem.href = "data:text/plain;charset=utf-8," + encodeURIComponent('test');
            //elem.href = window.URL.createObjectURL(blob);
            //elem.href = (window.URL ? URL : webkitURL).createObjectURL(blob);
            elem.download = 'test.txt';        
            document.body.appendChild(elem);
            elem.click();        
            document.body.removeChild(elem);
            //
            alert('?')
        }
    }
    DxioUser.prototype.login = function(username,password) {

        var hash = this.web3.utils.sha3(username)
        var kname = 'xio.user.'+hash

        if (!localStorage.getItem(kname)) {
            return this.createAccount(username,password)
        }
        var cryptedkey = JSON.parse( localStorage.getItem(kname) );
        this.account = this.web3.eth.accounts.decrypt(cryptedkey, password)

        address = this.account.address
        key = this.account.privateKey

        this.name = username
        this.address = this.account.address
        this.token = this.generateToken(this.account.privateKey)
        document.cookie = "token="+this.token+";path=/";
        // recuperation id + controle check address ====> via xio ou via blockchain ? blockchain first
        /*
        console.log(this.dapp)
        this.dapp._token = this.token
        this.dapp.get('user').then( function (data) {
            console.log(data)
        })
        */
        this.saveSession()
        return 
        return this.contract.request('about').then( function (about) {
            self.id = parseInt(about.userid)
            self.level = parseInt(about.level)
            self.saveSession()
            return self
        })
    }
    DxioUser.prototype.createAccount = function(username,password) {
       
        //this.dapp.request('REGISTER','user',{'email':email,'pasword':password}).then( function (resp) { alert(resp.content) } )

        var self = this

        var _createAccount = function(result) {
            console.log('REGISTER - CREATE ACCOUNT')

            //var newaccount = self.web3.eth.accounts.create()
            var seed = username+password
            //alert(seed)
            var key = self.web3.utils.sha3(seed)
            //alert(key)
            var newaccount = self.web3.eth.accounts.privateKeyToAccount(key)

            var cryptedkey = newaccount.encrypt(password)
            var hash = self.web3.utils.sha3(username)
            var kname = 'xio.user.'+hash
            localStorage.setItem( kname , JSON.stringify(cryptedkey));
            self.name = username
            self.hname = hash
            self.account = newaccount
            self.key = self.account.privateKey
            self.address = self.account.address
            alert(self.address)
        }

        var _registerAccount = function(result) {
            console.log('REGISTER - REGISTER ACCOUNT')
            return self.contract.request('registerUser',self.hname, '','')

            //.then( function (userid) {
            //    self.id = userid
            //    alert(self.id)
            //})
        }

        var _login = function() {
            console.log('REGISTER - LOGIN')
            return self.login(username,password)
        }

        var d = Promise.resolve({})
        d.then( _createAccount )
        //d.then( _registerAccount )
        d.then( _login )
        return d
    }
    DxioUser.prototype.register = function() {
        console.log('REGISTER - REGISTER ACCOUNT')
        var self = this
        this.key = this.unlock()
        this.contract.request('registerUser',self.hname, '','').then( function() {
            self.contract.request('about').then( function (about) {
                self.id = parseInt(about.userid)
                self.level = parseInt(about.level)
                self.saveSession()
            })
        })
    }
    DxioUser.prototype.unlock = function(password) {
        if (!this.key) {
            password = password || prompt('Please enter your password for private key access ?')
            var kname = 'xio.user.'+this.hname
            var cryptedkey = JSON.parse( localStorage.getItem(kname) );
            var account = this.web3.eth.accounts.decrypt(cryptedkey, password)
            //this.key = this.account.privateKey
            //alert('UNLOCKED '+this.account.address)
            return account.privateKey
        } else {
            return this.key
        }
        
    }
    DxioUser.prototype.generateToken = function(key) {
        var timestamp = Math.round((new Date()).getTime() / 1000) + 60*5;
        var nonce = timestamp.toString() // attention rique de fausse addresses coté serveur si int au lieu de string
        var sign = this.account.sign(nonce)
        var token = nonce+'-'+sign.v+'-'+sign.r+'-'+sign.s
        return token
    }
    DxioUser.prototype.logout = function() {
        this.clearSession()
        return Promise.resolve(this)
    }
    DxioUser.prototype.getCredit = function() {
        this.dapp.request('GETCREDIT','user', {}, function(data) {
            alert(data)
        })
    }
    DxioUser.prototype.send = function(address,value) {
        var self = this
        
        /*
        PB car confusion pour username non enregistré => send to $username implique que $username soit referencé
        -> risque de pb si un username existe deja (mas pas celui qu'on crois)
        */

        if (!address.startsWith('0x')) {
            alert('convert address')
            var hname = this.web3.utils.sha3(address)
            this.contract.request('getAddressOf',hname).then( function (address) {    
                if (address.startsWith('0x') && confirm('SEND '+value+' TO '+address)) {
                    return self.send(address,value)
                }    
                return false
            })
            return false
        }

        /* pas besoin de contract .. (sauf pour ne commission ou divers controle comme attente de paiement (eg factures))
        app.dapp.user.contract.request('sendValueTo',hname,{'value':value}).then( function (tx) {
            alert(tx)
        })
        */


        // any tool for validate address ??
        if (address.startsWith('0x00')) {
            alert ('bad address !')
            return
        }
        var params = {
            from: this.address,
            to: address,
            gas: 2000000,
            chainId: 1, 
            value: value
        }
        console.log('SEND '+address+' '+value+' .... params: ',params)
        
        var key = this.unlock()
        return this.web3.eth.accounts.signTransaction(params, key).then( function(signed) {
            return self.web3.eth.sendSignedTransaction(signed.rawTransaction).then( console.log )
        })
    }



/*
    DxioAccount = function(dapp,address,key) {
        address = address || null
        key = key || null

        this.dapp = dapp
        if (!address && !key) {
            var account = this.dapp.ethereum.web3.eth.accounts.create()
            address = account.address
            key = account.privateKey
        } else if (key) {
            var account = this.dapp.ethereum.web3.eth.accounts.privateKeyToAccount(key)
            address = account.address
            key = account.privateKey
        }
        this.address = address
        this.key = key
        this._account = account
    }
    DxioAccount.prototype.getBalance = function() {
        return this.dapp.ethereum.getBalance(this.address).then( function(data) { alert(data) } )  
    }
    DxioAccount.prototype.sign = function(message) {
        return this.dapp.ethereum.web3.eth.accounts.sign(message,this.key) // test suite au bug des addresses differentes
        //return this._account.sign(message) 
    }


    DxioAccount.prototype.sell = function() {
        this.dapp.contract.request('registerApp',{'name':'test','about':'abouttest','cost':12000,'_from': this.address}).then( function() { alert('ok') } )
    }
    DxioAccount.prototype.getsell = function() {
        // apps a proscript car ca peu etre un servive in vivo ... donc par une app => services 
        this.dapp.contract.request('getAppsProvided').then( function(data) { alert(data) } )
    }
    DxioAccount.prototype.buy = function() {
        alert(this.address)
    }
*/

    DxioAmount = function(value,currency) {
        this.value = value
        this.currency = currency || 'wei'  
        this.label = this.value+' '+this.currency    
        this.convert = function (currency_to) {
            return new DxioAmount(this.value,currency_to)    
        }
        return this
    }


    DxioApp = function(endpoint,config) {
        config = config || {}
        XioDapp.call(this, endpoint,config);
        this.ethereum = new Ethereum(config.web3)
        this.user = new DxioUser(this)
        var self = this
        $.getJSON( 'sdk/contracts/xio/latest/xio.json', function( data ) { 
            var netid = 'test'
            var address = data['addresses'][netid]
            var abi = data['abi']['Xio']
            self.contract = self.ethereum.registerContract('xio',abi,address)

        })          

    }
    DxioApp.prototype = Object.create(XioDapp.prototype, {
        constructor: { value: XioDapp }
    });
    DxioApp.prototype.getUserFromKey = function(key) {
        return new DxioUser(this,key)
    };
    DxioApp.prototype.amount = function(value,currency_from,currency_to) {
        currency_from = currency_from || 'wei'
        currency_to = currency_to || 'euro'
        return new DxioAmount(value,currency_from).convert(currency_to)
    };

	Dxio = function() {
		return this;
	};
	Dxio.prototype = {

		dapp: function(endpoint,config) { 
			return new DxioApp(endpoint,config)
		},

	}
	dxio = new Dxio();   

    Xio.prototype.network = function(uri) { 
        return new XioNetwork(uri)
    }

    Xio.prototype.user = function(kwargs) { 
        return new XioUser(kwargs)
    }

})();



