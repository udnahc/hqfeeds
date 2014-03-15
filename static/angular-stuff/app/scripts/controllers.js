angular.module('stockMarketApp').controller('AppCtrl', ['AlertService', 'UserService', function(AlertService, UserService) {
        var self = this;
        self.alertService = AlertService;
        self.userService = UserService;
        console.log("AppCtrl is initiated ");
    }]).controller("TopNavCtrl", [ 'UserService', function(UserService) {
        var self = this;
        self.loggedInUser = function() {
            return UserService.loggedInUserName();
        }
        console.log("Top Nav Ctrl is initiated ");
    }]). controller( 'FeedsDetailsCtrl', [ 'FeedsService', '$scope', function(FeedsService, $scope) {
        var self = this;
        self.detailed_feed_info = [];
        $scope.$on("UPDATE_FEED_DETAILS", function() {
            console.log("This should work now ");
            FeedsService.get_feeds_details_for_uri().success( function(detailed_feeds) {
                console.log("Detailed feeds here ", detailed_feeds);
                self.detailed_feed_info = detailed_feeds;
            })
        });
        FeedsService.get_feeds_details_for_uri().success( function(detailed_feeds) {
            console.log("Detailed feeds here ", detailed_feeds);
            self.detailed_feed_info = detailed_feeds;
        })
        console.log("Feeds Details Ctrl initiated ");

    }]).controller( 'FeedsInfoCtrl', [ 'FeedsService', function(FeedsService) {
        var self = this;
        self.feeds_info = [];
        FeedsService.get_feeds().success( function(feeds) {
            console.log(feeds);
            self.feeds_info = feeds;
        })

    }]).controller('LandingCtrl', ['StockService', function(StockService) {
        var self = this;
        self.stocks = [];
        StockService.query().success(function(stocks) {
            self.stocks = stocks;
        });

    }]).controller('AusthCtrl', ['AlertService', 'UserService', '$location', function(AlertService, UserService, $location) {
        var self = this;

        self.login = function() {
            UserService.login(self.username, self.password).then(function(user) {
                $location.path('/mine');
            }, function(err) {
                AlertService.set(err.msg);
            });
        };
        self.register = function() {
            UserService.register(self.username, self.password).then(function(user) {
                $location.path('/mine');
            }, function(err) {
                AlertService.set(err.data.msg);
            });
        };
    }]).controller('MyStocksCtrl', ['StockService', function(StockService) {
        var self = this;
        self.stocks = [];
        self.fetchStocks = function() {
            StockService.query().success(function(stocks) {
                self.stocks = stocks;
            });
        };
        self.fetchStocks();

        self.filters = {
            favorite: true
        };

        self.toggleFilter = function() {
            if (self.filters.favorite) {
                delete self.filters.favorite;
            } else {
                self.filters.favorite = true;
            }
        };

    }]).controller('LogoutCtrl', ['UserService', '$location', function(UserService, $location) {
        var redirect = function() {
            $location.path('/');
        };
        UserService.logout().then(redirect, redirect);
    }]);

