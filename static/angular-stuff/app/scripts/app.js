angular.module('stockMarketApp', ['ui.bootstrap','ui.router', "checklist-model"])
  .config(['$stateProvider', '$urlRouterProvider', function ($stateProvider,$urlRouterProvider) {

      var home= {
            name:'home',
            url:'/',
            templateUrl:"views/feed_details.html"
          },
          add_feed = {
              name:'add_feed',
              url: '/feed',
              templateUrl: "views/add_feed.html"
          },
          import_opml = {
              name:'import_opml',
              url: '/opml',
              templateUrl: "views/import_opml.html"
          }
      $stateProvider.state(home);
      $stateProvider.state(add_feed);
      $stateProvider.state(import_opml);
    }])
    .run(['$state', function ($state) {
        $state.transitionTo('home');
    }])

//      .when('/', {
//      templateUrl: 'views/hqFeeds.html',
//      resolve: {
//                auth: ['UserService', 'AlertService', '$q', '$location', function(UserService, AlertService, $q, $location) {
//                    console.log("Resolution working ? ");
//                    return UserService.loggedInUserInfo().then(function(success) {}, function(err) {
//                        AlertService.set('Please login to access your information');
//                        $location.path('/login');
//                        return $q.reject(err);
//                    });
//                }]
//            }
//      })
//      .when('/feed/add', {
//            templateUrl: 'views/add_feed.html',
//            controller: 'AddFeedCtrl'
//        })
//      .when('/login', {
//        templateUrl: 'views/login.html',
//        controller: 'AuthCtrl',
//        controllerAs: 'loginCtrl'
//      })
//      .when('/register', {
//        templateUrl: 'views/signup.html',
//        controller: 'AuthCtrl',
//        controllerAs: 'signupCtrl'
//      })
//      .when('/mine', {
//        templateUrl: 'views/mine.html',
//        controller: 'MyStocksCtrl',
//        controllerAs: 'myStocksCtrl',
//        resolve: {
//          auth: ['UserService', 'AlertService', '$q', '$location', function(UserService, AlertService, $q, $location) {
//            return UserService.tokens().then(function(success) {}, function(err) {
//              AlertService.set('Please login to access your information');
//              $location.path('/login');
//              return $q.reject(err);
//            });
//          }]
//        }
//      })
//      .when('/logout', {
//        template: ' ',
//        controller: 'LogoutCtrl'
//      })
//      .otherwise({
//        redirectTo: '/'
//      });
//    }]);
