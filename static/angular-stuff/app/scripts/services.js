angular.module('stockMarketApp')
    .factory('AlertService', function() {
        var message;
        return {
            set: function(msg) {
                message = msg;
            },
            clear: function() {
                message = null;
            },
            get: function() {
                return message;
            }
        };
    }).factory('StockService', ['$http', function($http) {
        return {
            query: function() {
                return $http.get('/api/stocks');
            },
            get: function(code) {
                return $http.get('/api/stocks/' + code);
            }
        };
    }]).factory('UserService', ['$http', '$q', function($http, $q) {
        var user = {};
        var loggedIn = false;
        var loginSuccess = function(resp) {
            user = resp.data.user;
            loggedIn = true;
            return user;
        };
        var loginFailure = function(err) {
            loggedIn = false;
            return $q.reject(err.data);
        };

        return  {
            loggedInUserName : function( ){
                return user.logged_in_user;
            },
            loggedInUserInfo: function() {
                return $http.get('http://localhost:5000/get_logged_in_user_info').then(function(user_info_response) { user=user_info_response.data}, function() { console.log("No user is logged in ");});
            },
            isLoggedIn: function() {
                return loggedIn;
            },
            login: function(username, pwd) {
                return $http.post('/api/login', {username: username, password: pwd}).then(loginSuccess, loginFailure);
            },
            logout: function() {
                return $http.post('/api/logout', {}).then(function() {loggedIn = false;}, function() {loggedIn = false});
            },
            register: function(username, pwd) {
                return $http.post('/api/register', {username: username, password: pwd}).then(loginSuccess, loginFailure);
            },
            tokens: function() {
                if (loggedIn) {
                    return $q.when(user);
                } else {
                    return $http.post('/api/token', {}).then(loginSuccess, loginFailure);
                }
            }
        };
    }]).factory('FeedsService', ['$http', function($http) {
        var feeds_info = {};
        var currently_reading_uri = "";

        return {
            set_feed_uri : function(uri) {
              currently_reading_uri =  uri;
            },
            get_feed_uri : function() {
              return currently_reading_uri;
            },
            get_feeds: function() {
                return $http.get('http://localhost:5000/get_feeds_for_user');
            },
            get_latest_feeds_for_default_view: function() {
                return $http.get('http://localhost:5000/get_top_stories_for_user');
            },
            get_feeds_details_for_uri : function() {
                if ( currently_reading_uri ) {
                    console.log("Showing feeds for ", currently_reading_uri);
                    return $http.post('http://localhost:5000/fetch_feeds_for_url', {feed_uri: currently_reading_uri });
                } else {
                    console.log("Showing the default page !! ");
                    return $http.get('http://localhost:5000/get_top_stories_for_user');
                }
            },
            get: function() {
                return feeds_info;
            }
        };
    }]);
