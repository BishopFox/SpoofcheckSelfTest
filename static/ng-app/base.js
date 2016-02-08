var app = angular.module('spoofcheck', ['ngRoute', 'ngAnimate', 'ngWebSocket']);

app.config( ['$routeProvider', '$locationProvider',
        function($routeProvider, $locationProvider) {
            $routeProvider.when(
                '/', {
                    templateUrl: '/static/ng-app/home.html',
                    controller: 'HomeController'
                }
            ).when(
                '/watch', {
                    templateUrl: '/static/ng-app/watch.html',
                    controller: 'WatchController'
                }
            ).when(
                '/report/:domain', {
                    templateUrl: '/static/ng-app/report.html',
                    controller: 'ReportController'
                }
            ).otherwise({
                redirectTo: '/'
            })
            ;
        }

])
    .constant('EVENTS', {
        output: 'output',
        sent: 'sent'
    })
;

app
    .factory('MonitorWebSocket', ['$websocket', 'EVENTS', '$rootScope',
        function($websocket, EVENTS, $rootScope) {
            console.log("Activated websocket");
            var ws = $websocket("ws://" + location.host + "/connect/monitor");
            var output = [];

            ws.onMessage(function(message) {
                var data = JSON.parse(message.data);
                console.log(message);

                // Routing
                if (data.opcode != "Error") {
                    output.push(data.message);
                    $rootScope.$broadcast(EVENTS.output);
                    console.log(output);
                }

            });

            return {
                output: output,
                checkDomain: function(domain) {
                    ws.send(JSON.stringify(
                        {
                            opcode: 'check',
                            domain: domain
                        }
                    ));
                }
            };


        }
    ])
;

app
    .controller('HomeController', ['$scope', '$rootScope', 'MonitorWebSocket', '$location', 'EVENTS',
        function($scope, $rootScope, MonitorWebSocket, $location, EVENTS) {
            $rootScope.domain = undefined;

            $scope.checkDomain = function(domain) {
                console.log("Firing checkDomain with " + domain);
                $rootScope.domain = domain;
                $rootScope.ws = MonitorWebSocket;

                $rootScope.$on(EVENTS.output, function(evt, data) {
                    console.log(evt);
                    $location.path("/report/" + $rootScope.domain).replace();
                });

                $rootScope.ws.checkDomain(domain);

                $location.path("/watch");
                $rootScope.$broadcast(EVENTS.sent);
            }
        }
    ])

    .controller('WatchController', ['$scope', '$rootScope', '$location', 'EVENTS',
        function($scope, $rootScope, $location, EVENTS) {
            console.log("Loading watch controller");
            if ($rootScope.ws === undefined || $rootScope.domain === undefined) {
                $location.path("/");
            }


        }
    ])

    .controller('ReportController', ["$scope", '$rootScope', "$location", "$routeParams", "MonitorWebSocket", "EVENTS",
        function($scope, $rootScope, $location, $routeParams, MonitorWebSocket, EVENTS) {
            console.log($routeParams.domain);
            if ($rootScope.ws === undefined || $rootScope.domain === undefined
                || $rootScope.domain !== $routeParams.domain) {
                if ($routeParams.domain !== null && $routeParams.domain !== undefined) {
                    $rootScope.domain = $routeParams.domain;
                    $rootScope.ws = MonitorWebSocket;
                    $rootScope.ws.checkDomain($rootScope.domain);
                    $rootScope.$on(EVENTS.output, function(evt, data) {
                        console.log(evt);
                        $location.path("/report/" + $rootScope.domain).replace();
                    });
                    $location.path("/watch");
                } else {
                    $location.path("/");
                }
            }
            $scope.message = $rootScope.ws.output[$rootScope.ws.output.length - 1];
        }
    ])
;