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
            loggedInUser: function() {
                return user;
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
        var currently_reading_label = "";
        var currently_reading_feed_label = "";
        var feed_labels = "";

        return {
            set_feed_uri : function(uri, label, feed_label) {
              currently_reading_uri =  uri;
              currently_reading_label = label;
              currently_reading_feed_label = feed_label;
            },
            get_currently_reading_label: function() {
                return currently_reading_label
            },
            get_currently_reading_feed_label: function() {
                return currently_reading_feed_label
            },
            add_feed_with_tags: function(feed_details) {
                console.log("This needs to be posted ", feed_details);
                $http.post('http://localhost:5000/add_tag', feed_details);
            },
            get_feed_uri : function() {
              return currently_reading_uri;
            },
            return_feed_labels : function() {
              return feed_labels;
            },
            create_entries_through_opml: function(opmlFile) {
                var fd = new FormData();
                fd.append('file', opmlFile);
                console.log(fd);
                $http.post('http://localhost:5000/upload_opml_file', fd ,{
                    transformRequest: angular.identity,
                    headers: {'Content-Type': undefined}
                });
            },
            get_feeds: function() {
                return $http.get('http://localhost:5000/get_feeds_for_user');
            },
            get_latest_feeds_for_default_view: function() {
                return $http.get('http://localhost:5000/get_top_stories_for_user');
            },
            get_feed_categories_for_user: function() {
                return $http.get("http://localhost:5000/get_feed_labels_for_user").then(
                        function(feed_labels_response) { feed_labels = feed_labels_response.data;},
                        function() { console.log("Error in getting feed labels for user");
                        }
                );
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
