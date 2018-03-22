




app.services.bind('ethereum',{
	handler: 'xrn:inxio:ethereum'
})



app.angular.directive('ethinfo', function($timeout) {
    return {
        restrict: 'E',
        scope: {
            'type': '@',
            'address': '@',
            'account': '@',
            'contract': '@',
            'tx': '@'
        },
        link: function(scope, element, attrs, ctrl,transclude) {
            var network = 'ropsten'
            var path = 'address'
            var address = attrs.address
            if (attrs.address) {
                scope.type = 'address'
                scope.href = 'https://'+network+'.etherscan.io/'+path+'/'+attrs.address  
                scope.value = attrs.address  
            }
            if (attrs.account) {
                scope.type = 'account'
                scope.href = 'https://'+network+'.etherscan.io/'+path+'/'+attrs.account
                scope.value = attrs.account  
            }
            if (attrs.contract) {
                scope.type = 'contract'
                scope.href = 'https://'+network+'.etherscan.io/'+path+'/'+attrs.contract
                scope.value = attrs.contract  
            }

        },
        template: '<span><tag label="{{type}}"><b>{{type}}</b></tag> <a href="{{href}}" target="_blank">{{value}}</a></span>',
    }
});  

app.angular.directive('ethereum', function($timeout) {
    return {
        restrict: 'E',
        scope: true,
        controller: ['$scope','$element','$q',function ($scope,$element,$q) {   
            this.ethereum = ethereum
            this.getBalance = function() {
                this.ethereum.getBalance( function (data) { 
                    alert(data) 
                })    
            }
        }],
        link: function(scope, element, attrs, ctrl,transclude) {
        },
        controllerAs: 'ethereum',
        template: '<div><a href="javascript:" ng-click="ethereum.getBalance()">get balance</a></div>',
    }
});  


app.angular.directive('contract', function($timeout,$q) {
    return {
        restrict: 'E',
        scope: true,
        controller: ['$scope','$element','$q',function ($scope,$element,$q) { 
            this.ethereum = ethereum
            this.transactions = []
            this.events = []
            this.init = function(name) {
                this.name = name
                this.contract = this.ethereum.contracts[this.name]
                this.abi = this.contract.abi
                this.address = this.contract.address
                this.getTransactions()
                this.getEvents()
            }
            var self = this
            this.getTransactions = function() {
                this.contract.getTransactions().done(function(data) {
                    self.transactions = [data]
                })  
            }
            this.getEvents = function() {
                this.contract.getEvents().done(function(data) {
                    self.events = [data]
                })
            }
            this.setEstimate = function(estimate) {
                this.estimate = estimate
            }
            this.submit = function($event,config) {
                console.log( $event.target)
                var type = config.type
                var method = config.name
                var payload = {}
                var form = $($event.target).closest('form')

                $.each( form.serializeArray() , function(i, obj) { payload[obj.name] = obj.value })

                console.log(type)
                console.log(method)
                console.log(payload)
                if (this.estimate) {
                    return this.contract.estimate(method,payload,function(error,result) {
                        console.log('contract response')
                        console.log(result)
                    })
                } else {
                    return this.contract.request(method,payload,function(error,result) {
                        console.log('contract response')
                        console.log(result)
                    }) 
                }

            }
        }],
        link: function(scope, element, attrs, ctrl,transclude) {
            ctrl.init( attrs.name )
        },
        controllerAs: 'contract',
        template: `<card view="map.function">
            <header>
                <h1>contract: {{contract.name}}</h1>
                <h4><ethinfo account="{{contract.ethereum.account}}"><ethinfo></h4>
                <h4><ethinfo contract="{{contract.address}}"><ethinfo></h4>

                <button view="map.function" label="functions"></button>
                <button view="map.event" label="events"></button>
                <button view="abi" label="abi"></button>
                <button view="txs" label="transactions"></button>
                <button view="logs" label="logs"></button>
            </header>
            <section ng-if="view=='map'">

                <list>
                    <item ng-repeat="row in contract.abi" ng-if="row.type==subview">
                        <card>
                            <header>
                                <h3><tag>{{row.type}}</tag> {{row.name}}
                                    <small>
                                        <tag ng-if="row.payable">payable</tag>
                                        <tag ng-if="row.constant">constant</tag>
                                    </small>
                                </h3>

                            </header>
                            <section class="row">
                                <fieldset class="col-md-4">
                                    <legend>INPUT</legend>
                                    <form ng-submit="contract.submit($event,row)">
                                        <field ng-repeat="input in row.inputs" name="{{input.name}}" label="{{input.name}}" required="true" placeholder="{{input.type}}"></field>    
                                        <field name="_value" label="amount" type="number" required="true" ng-if="row.payable"></field>
                                        <button class="btn btn-primary"  label="SUBMIT" ng-click="contract.setEstimate(false)"></button>
                                        <button class="btn btn-default"  label="ESTIMATE" ng-click="contract.setEstimate(true)"></button>
                                    </form>  
                                </fieldset>
                                <fieldset class="col-md-4">
                                    <legend>OUTPUT</legend>
                                    <ul>
                                        <li ng-repeat="output in row.outputs">{{output.name}} {{output.type}}</li>
                                    </ul>  
                                </fieldset>
                                <fieldset class="col-md-4">
                                    <code>{{row}}</code>
                                </fieldset>
                            </section>
                        </card>
                    </item>
                </list>
            </section>
            <section ng-if="view=='abi'">
                {{contract.abi}}
            
            </section>
            <section ng-if="view=='txs'">
                TRANS
                <table>
                    <tr ng-repeat="row in contract.transactions"><td>{{row}}</td></tr>
                    
                </table>
            
            </section>

            <section ng-if="view=='logs'">
                events
                <table>
                    <tr ng-repeat="row in contract.events"><td>{{row}}</td></tr>
                    
                </table>
            
            </section>

            <footer>
            
            </footer>

            </card>

        `,
    }
});  

/*

    eth = ethereum()
    app.get('fake/contracts/digitalworker').then( function(data) {
        eth.registerContract('digitalworker',data['address'],data['abi'])
        var template = $('#template-contract-abi')
        var html = template.render(data['abi'])
        $('#abi').html(html)
    })


    $(document).find('button[data-web3-action]').click(function() {
        var action = $(this).data('web3-action')  
        f7.app.confirm('Confirmez vous cette action ?',action,function() {
            contract.execute(action)
        })
    })

            var nfo = action.split('/')
            var contract = eth.contracts[nfo[0]]
            var method = nfo[1]
            alert(contract[method])
*/
