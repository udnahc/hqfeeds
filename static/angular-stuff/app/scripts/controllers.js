angular.module('stockMarketApp').controller('AppCtrl', ['AlertService', 'UserService', '$state', function(AlertService, UserService , $state) {
        var self = this;
        self.alertService = AlertService;
        self.userService = UserService;
        console.log("AppCtrl is initiated ");

        self.setPage = function (page) {
            $state.transitionTo(page);
        };

    }]).controller("TopNavCtrl", [ 'UserService', function(UserService) {
        var self = this;
        self.loggedInUser = function() {
            return UserService.loggedInUserName();
        }
        console.log("Top Nav Ctrl is initiated ");
    }]). controller( 'FeedsDetailsCtrl', [ 'FeedsService', '$scope', '$state', function(FeedsService, $scope) {
        var self = this;
        self.detailed_feed_info = [];

        self.currently_reading_label = "";

        $scope.$on("UPDATE_FEED_DETAILS", function() {
            console.log("This should work now ");
            self.currently_reading_label = FeedsService.get_currently_reading_label();
            self.currently_reading_feed_label = FeedsService.get_currently_reading_feed_label();
            FeedsService.get_feeds_details_for_uri().success( function(detailed_feeds) {
                console.log("Detailed feeds here ", detailed_feeds);
                self.detailed_feed_info = detailed_feeds;
            })
        });
        FeedsService.get_feeds_details_for_uri().success( function(detailed_feeds) {
            console.log("Detailed feeds here ", detailed_feeds);
            self.detailed_feed_info = detailed_feeds;
            self.currently_reading_label = "Top Stories "
        })
        console.log("Feeds Details Ctrl initiated ");

    }]).controller( 'FeedsInfoCtrl', [ 'FeedsService', function(FeedsService) {
        var self = this;
        self.feeds_info = [];

        FeedsService.get_feeds().success( function(feeds) {
            console.log(feeds);
            self.feeds_info = feeds;
        })

    }]).controller( 'AddFeedCtrl', [ 'UserService', 'FeedsService','$scope', function(UserService,FeedsService,$scope) {

        console.log("Initializing Add Feed Ctrl ");
        var self = this;

        $scope.feed_tags = [];

        self.feed = {
            custom_feeds_tags: "",
            feed_url: ""
        }

        FeedsService.get_feed_categories_for_user();

        self.items = FeedsService.return_feed_labels();
        console.log("Feed Labels " , self.items);

        self.ok = function(feed) {
            feed.feed_tags = feed.feed_tags.concat(feed.custom_feed_tags.split(','));
            console.log("This is feed url to be added ", feed.feed_url);
            FeedsService.add_feed_with_tags(feed);
        }
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

    }]).controller( 'OPMLImportCtrl', [ 'FeedsService', '$scope', function(FeedsService,$scope) {
        console.log("Initializing OPML Import ctrl ");
        var self = this;

        $scope.setFile = function(myFile) {
            console.log("File to be parsed ", myFile);
            self.myFile = myFile;
        };

        self.parseOpml = function () {
            console.log("Parse this opml file ");
            var file = self.myFile;
            FeedsService.create_entries_through_opml(file);
        };

        self.cancel = function () {
            console.log("Should cancel the file chosen ");
        };
    }]);

