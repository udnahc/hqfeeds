var hqFeedsApp = angular.module("hqFeedsApp", []);

hqFeedsApp.config(function($httpProvider, $routeProvider){
    delete $httpProvider.defaults.headers.common['X-Requested-With'];
    console.log('Reached config ');
    
    $routeProvider
            .when( '/login', 
                   { controller: 'LoginController', templateUrl: 'Partials/login.html' }
                 )
            .when( '/logout', 
                   { controller: 'TopNavController', templateUrl: 'Partials/logout.html' }
                 )
            .when( '/content',
                   { controller: 'TopNavController',templateUrl: 'Partials/content.html' }
                 )
            .otherwise( { redirectTo: '/login'})

    console.log("Done with the config ");
});

hqFeedsApp.controller("LoginController", function($scope, $http, $location){
    $scope.content = "Please login for accessing these URI's ";
    $scope.twitter_url = "http://127.0.0.1:5000/login_with_twitter";
        
    $scope.callTwitterAuth = function() {
        $http.get($scope.twitter_url)
            .then(function(result){
                $scope.authorization_details = result.data;
                console.log($scope.authorization_details);
                if ( $scope.logged_in_user_details.login == false )  {
                    console.log("User is not logged in !! ");
                    
                    $location.path("/login");
                } else {
                    console.log("User is logged in !! ");
                    $location.path("/content");                
                }
            
            });
    }

});

hqFeedsApp.controller("TopNavController", function($scope, $http, $location) {

    $scope.url = "http://127.0.0.1:5000/get_logged_in_user_info";
    $scope.logged_in_user_details = {};

    $scope.logout_url = "http://127.0.0.1:5000/logout";
    $scope.logout_message = "default message";

    $scope.logout = function() {
        $http.get($scope.logout_url)
            .then(function(result){
                $scope.logout_message = result.data;
                console.log("This is the logout message " + result);
                $location.path("/logout");                
            });
    }
   
    $scope.fetchContent = function() {
        $http.get($scope.url).then(function(result){
            $scope.logged_in_user_details = result.data;
            
            // if ( $scope.logged_in_user_details.is_user_logged == false )  {
            //     console.log("User is not logged in !! ");
            //     $location.path("/login");
            // }
            
        });
    }
    
    $scope.fetchContent();
});

hqFeedsApp.controller("LeftNavController", function($scope) {
    $scope.left_nav_info = 'Left Nav Info';
});

hqFeedsApp.controller("CenterScreenController", function($scope) {
    $scope.reader_content = 'Reader Content';
});