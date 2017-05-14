var app = angular.module('spoofcheck', ['ngRoute', 'ngAnimate', 'ngWebSocket', 'vcRecaptcha']);

app.config( ['$routeProvider', '$locationProvider', 'vcRecaptchaServiceProvider',
        function($routeProvider, $locationProvider, vcRecaptchaServiceProvider) {
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
                '/report', {
                    templateUrl: '/static/ng-app/report.html',
                    controller: 'ReportController'
                }
            ).otherwise({
                redirectTo: '/'
            })
            ;

            // TODO: Fix to pull from config file, or modify in production
            vcRecaptchaServiceProvider.setSiteKey("6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI");
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
                checkDomain: function(domain, captchaResponse) {
                    var data = JSON.stringify(
                        {
                            opcode: 'check',
                            domain: domain,
                            captchaResponse: captchaResponse
                        }
                    );

                    console.log(data);
                    ws.send(data);
                }
            };


        }
    ])
;

app
    .controller('HomeController', ['$scope', '$rootScope', 'MonitorWebSocket', '$location', 'EVENTS',
        function($scope, $rootScope, MonitorWebSocket, $location, EVENTS) {
            $rootScope.domain = undefined;

            $scope.response = null;
            $scope.widgetId = null;

            $scope.setResponse = function (response) {
                console.info('Response available: %s', response);
                $scope.captchaResponse = response;
            };
            $scope.setWidgetId = function (widgetId) {
                console.info('Created widget ID: %s', widgetId);
                $scope.widgetId = widgetId;
            };

            $scope.checkDomain = function(domain) {
                console.log("Firing checkDomain with " + domain);
                var parsedDomain = domain;
                var emailRegex = /@([\w.]+)/;
                var emailRegexOut = domain.match(emailRegex);
                if (emailRegexOut != null) {
                    parsedDomain = emailRegexOut[1];
                }

                $rootScope.domain = parsedDomain;
                $rootScope.ws = MonitorWebSocket;

                $rootScope.$on(EVENTS.output, function(evt, data) {
                    console.log(evt);
                    $location.path("/report").replace();
                });

                $rootScope.ws.checkDomain(domain, $scope.captchaResponse);

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


    .controller('ReportController', ["$scope", '$rootScope', "$location",
        function($scope, $rootScope, $location) {
            if ($rootScope.ws === undefined || $rootScope.domain === undefined) {
                $location.path("/");
            } else {
                $scope.message = $rootScope.ws.output[$rootScope.ws.output.length - 1];
            }
        }
    ])
;