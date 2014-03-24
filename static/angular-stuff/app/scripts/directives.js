angular.module('stockMarketApp').directive('stockWidget', ['StockService', 'UserService', '$interval',
        function(StockService, UserService, $interval) {
            return {
                restrict: 'A',
                templateUrl: 'views/stock-widget.html',
                scope: {
                    stockData: '=',
                    whenToggle: '&'
                },
                link: function($scope, $element, $attrs) {
                    $scope.getChange = function() {
                        return Math.ceil((($scope.stockData.price - $scope.stockData.previous) / $scope.stockData.previous) * 100);
                    };
                    $scope.getChangeClass = function() {
                        return {
                            positive: $scope.stockData.price > $scope.stockData.previous,
                            negative: $scope.stockData.price <= $scope.stockData.previous
                        }
                    };
                    $scope.toggleFavorite = function() {
                        StockService.toggleFavorite($scope.stockData.ticker).then(function(stocks) {
                            if ($scope.whenToggle) {
                                $scope.whenToggle();
                            }
                        }, function(err) {});
                    };
                    $scope.shouldShowButtons = function() {
                        return UserService.isLoggedIn();
                    };

                    var fetchStockDetail = function() {
                        StockService.get($scope.stockData.ticker).success(function(stockData) {
                            $scope.stockData.history = stockData.history;
                            $scope.stockData.price = stockData.price;
                            $scope.stockData.previous = stockData.previous;
                        });
                    };
                    $interval(fetchStockDetail, 5000);
                }

            };
        }]).directive('lineChart', ['$timeout', '$window', function($timeout, $window) {
        return {
            restrict: 'A',
            scope: {
                graphData: '='
            },
            link: function($scope, $element, $attrs) {
                var checkAndContinue = function() {
                    if ($window.googleChartsLoaded) {
                        drawChart();
                    } else {
                        $timeout(checkAndContinue, 500);
                    }
                };

                var dataToArray = function(priceHistory) {
                    var arr = [['Index', 'Price']];
                    for (var i = 0; i < priceHistory.length; i++) {
                        arr.push([i, priceHistory[i]]);
                    }
                    return arr;
                };

                var drawChart = function() {
                    var chart = new google.visualization.LineChart($element[0]);
                    $scope.$watch('graphData', function(newVal) {
                        if (newVal) {
                            chart.draw(google.visualization.arrayToDataTable(dataToArray(newVal)), {
                                height: 70,
                                legend: {position: 'none'}
                            });
                        }

                    }, true);
                };
                checkAndContinue();

            }
        };
    }]).directive('feedDetails', ['UserService', 'FeedsService', '$sce',
        function(UserService,FeedsService, $sce) {
            return {
                restrict: 'A',
                templateUrl: 'views/feed_details_widget.html',
                scope: {
                    feedDetailsData: '='
                },
                link: function($scope, $element, $attrs) {
                    $scope.sanitize_description = function() {
                            return $sce.trustAsHtml($scope.feedDetailsData.description);
                    };
                }
            };
        }]).directive('feedInfo', ['UserService', 'FeedsService','$rootScope', '$interval',
        function(UserService,FeedsService, $rootScope, $interval) {
            return {
                restrict: 'A',
                templateUrl: 'views/feeds_info_widget.html',
                scope: {
                    feedInfoData: '='
                },
                link: function($scope, $element, $attrs) {
                    $scope.show_feed = function() {
                        return $scope.feed_info_data;
                    };

                    $scope.get_feeds_for_uri = function(uri_info, uri_label, feed_label) {
                        console.log("This is the URI to be obtianed " , uri_info);
                        FeedsService.set_feed_uri (uri_info, uri_label, feed_label);
                        $rootScope.$broadcast("UPDATE_FEED_DETAILS","");
                        console.log("Emitting signal to update changes everywhere ");
                    };

//                    $interval(function() {
//                        console.log("Fetching and updating any feed updates !! ");
//                        $rootScope.$broadcast("UPDATE_FEED_DETAILS","");
//                    }, 50000);

                }
            };
        }]).directive('fileModel', ['$parse', function ($parse) {
        return {
            restrict: 'A',
            link: function($scope, $element, $attrs) {
                var model = $parse($attrs.fileModel);
                var modelSetter = model.assign;

                $element.bind('change', function(){
                    $scope.$apply(function(){
                        modelSetter($scope, $element[0].files[0]);
                        $scope.setFile($scope.myFile);
                    });
                });
            }
        };
        }]);