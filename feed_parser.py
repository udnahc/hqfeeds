from flask import (Flask, redirect, url_for, session, render_template, flash,
                   request, make_response, g)
from flask.ext.oauth import OAuth
import simplejson as json
import requests
import os
import opml
import datetime
import pymongo
import logging
from collections import defaultdict
import feedparser

from mongo_stuff import MongoLib

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# import config from $APP_CONFIG file

app.config.from_envvar('APP_CONFIG')  # export APP_CONFIG=/path/to/settings.cfg
app.secret_key = app.config['SECRET_KEY']

oauth = OAuth()
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={
                              'scope': 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile http://www.google.com/reader/api/0/subscription/list',
                              'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type':
                                               'authorization_code'},
                          consumer_key=app.config['GOOGLE_CLIENT_ID'],
                          consumer_secret=app.config['GOOGLE_CLIENT_SECRET'])
# twitter oauth2 setup
twitter = oauth.remote_app('twitter',
                           base_url='https://api.twitter.com/1/',
                           request_token_url='https://api.twitter.com/oauth/request_token',
                           access_token_url='https://api.twitter.com/oauth/access_token',
                           authorize_url='https://api.twitter.com/oauth/authenticate',
                           consumer_key=app.config['TWITTER_CLIENT_ID'],
                           consumer_secret=app.config['TWITTER_CLIENT_SECRET']
                           )

# This has to be initiated before request to make sure there is a fresh object everytime a request is made.
mongo_lib = None

@app.before_request
def before_request():
    g.user = None
    global mongo_lib
    mongo_lib = MongoLib()
    if 'user' in session:
        g.user = session['user']


@app.after_request
def after_request(response):
    # Invalidating the mongo lib object
    global mongo_lib
    mongo_lib = None
    return response


@google.tokengetter
def get_access_token():
    return session.get('access_token')


@app.route('/', methods=['GET'])
#@login_required
def data_index():
    return redirect(url_for('view_feed_entries'))


@app.route('/get_logged_in_user_info', methods=['GET'])
def get_user_info():
    if g.user:
        user_info = {'is_user_logged': True, 'logged_in_user': g.user['user_name']}
    else:
        user_info = {'is_user_logged': False}

    # TODO: This has to be removed post fixing login issues !!!!
    #user_info = {'is_user_logged': True, 'logged_in_user': 'Chandrashekar', 'logged_in_user_id':'some_id'}
    # TODO: This has to be removed post fixing login issues !!!!
    return json.dumps(user_info)


@app.route('/show_feed_entries/', methods=['POST'])
#@login_required
def feed_entries():
    import feedparser
    entries = None
    feed_name = None
    url = None
    entries_count = 0
    if request.method == "POST":

        from pymongo import MongoClient
        client = MongoClient()
        client = MongoClient('localhost', 27017)

        db = client.feeds
        collection = db.feeds_dump
        url = request.form['url']

        feed_name = request.form['feed_name']
        if url:
            entries = collection.find({"xmlUrl": url}).sort(
                "parsed_time", pymongo.DESCENDING)
            entries_count = entries.count()

        return render_template('feed_info.html', entries=entries, feed_name=feed_name, url=url, entries_count=entries_count)


@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    """Called after authorization.  After this function finished handling,
    the OAuth information is removed from the session again.  When this
    happened, the tokengetter from above is used to retrieve the oauth
    token and secret.

    Because the remote application could have re-authorized the application
    it is necessary to update the values in the database.

    If the application redirected back after denying, the response passed
    to the function will be `None`.  Otherwise a dictionary with the values
    the application submitted.  Note that Twitter itself does not really
    redirect back unless the user clicks on the application name.
    """

    if resp is None:
        return json.dumps({'login': False})

    user = User.query.filter_by(name=resp['screen_name']).first()

    # user never signed on
    if user is None:
        user = User(name=resp['screen_name'])
        dbsession.add(user)

    # in any case we update the authenciation token in the db
    # In case the user temporarily revoked access we will have
    # new tokens here.
    user.oauth_token = resp['oauth_token']
    user.oauth_secret = resp['oauth_token_secret']
    dbsession.commit()
    session['user_id'] = user.id
    return redirect(url_for('view_feed_entries'))


@twitter.tokengetter
def get_twitter_token():
    """This is used by the API to look for the auth token and secret
    it should use for API calls.  During the authorization handshake
    a temporary set of token and secret is used, but afterwards this
    function has to return the token and secret.  If you don't want
    to store this in the database, consider putting it into the
    session instead.
    """
    user = g.user
    if user is not None:
        return user.oauth_token, user.oauth_secret


@app.route('/login')
def login():
    """Calling into authorize will cause the OpenID auth machinery to kick
    in.  When all worked out as expected, the remote application will
    redirect back to the callback URL provided.
    """
    return render_template('login.html')


@app.route('/loginaction')
def loginaction():
    if request.args.get('logintype') == "twitter":
        return twitter.authorize(callback=url_for('oauth_authorized',
                                                  next=request.args.get('next') or request.referrer or None))
    else:
        return google.authorize(callback=url_for('google_callback', _external=True))


def login_or_create_user(json_data):
    from pymongo import MongoClient
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    db = client.feeds
    collection = db.user_info

    # Check if the user exists in the mongo db
    user_info = collection.find_one({'user_email': json_data['email']})
    if not user_info:
        # Else create a profile for this user
        user_data = {"user_name": json_data['name'], "user_email": json_data['email'], "last_logged_in": datetime.datetime.now()}
        collection.insert(user_data)
        user_info = collection.find_one({'user_email': json_data['email']})
        session['user'] = user_info
        login_user(user_info)
    else:
        # If yes log the user in
        session['user'] = user_info
        print session
    return user_info

@app.route(app.config['REDIRECT_URI'])
@google.authorized_handler
def google_callback(resp):
    """
    """
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    if access_token:
        googleaccess = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            headers={'Authorization': 'OAuth ' + access_token})

    jsondata = googleaccess.json()

    user_info = login_or_create_user(jsondata)
    user_info["_id"] = str(user_info["_id"] )
    user_info["last_logged_in"] = str(user_info["last_logged_in"])
    return json.dumps(user_info)


@app.route('/login_with_twitter')
def login_with_twitter():
    """Calling into authorize will cause the OpenID auth machinery to kick
    in.  When all worked out as expected, the remote application will
    redirect back to the callback URL provided.
    """
    some_return_value = twitter.authorize(callback=url_for('oauth_authorized'))
    return some_return_value


@app.route('/thanks')
def thanks():
    return render_template('thanks.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user', None)
    return json.dumps({'status': 'done'})


@app.route('/add_feed', methods=['POST'])
#@login_required
def add_feed():
    uri = request.data
    from tasks.read_update_feed import check_and_parse_feed
    check_and_parse_feed(uri)
    return_dict = {uri: "created"}
    return json.dumps(return_dict)


@app.route('/subscribe', methods=['POST'])
#@login_required
def subscribe():
    input_dict = json.loads(request.data)
    from pymongo import MongoClient
    client = MongoClient()
    client = MongoClient('localhost', 27017)

    db = client.feeds
    collection = db.user_feeds_map
    collection.update({'user_name': input_dict['user_name']}, {"$addToSet": {
                      'listOfFeeds.default': input_dict['feed_name']}}, upsert=True)
    from tasks.read_update_feed import check_and_parse_feed
    check_and_parse_feed(input_dict['feed_name'])

    return json.dumps({"value": "created"})


@app.route('/add_tag', methods=['POST'])
#@login_required
def add_tag():
    input_dict = json.loads(request.data)
    tags = input_dict['feed_tags']
    uri = input_dict['feed_url']

    user_name = g.user['user_email']

    for tag in tags:
        from pymongo import MongoClient
        client = MongoClient()
        client = MongoClient('localhost', 27017)

        db = client.feeds
        collection = db.user_feeds_map
        collection.update({'user_name': user_name},
                          {"$addToSet": {'listOfFeeds.%s' % tag: uri}}, upsert=True)
    return json.dumps({'info': 'tags_added'})


@app.route('/remove_tag', methods=['POST'])
#@login_required
def remove_tag():
    input_dict = json.loads(request.data)
    tags = input_dict['tags']
    uri = input_dict['feed_name']
    user_name = input_dict['user_name']

    for tag in tags:
        from pymongo import MongoClient
        client = MongoClient()
        client = MongoClient('localhost', 27017)

        db = client.feeds
        collection = db.user_feeds_map
        collection.update({'user_name': input_dict['user_name']},
                          {"$pull": {'listOfFeeds.%s' % tag: uri}}, upsert=True)
    return json.dumps({'info': 'tags_removed'})


@app.route('/get_feeds_for_user', methods=['GET'])
#@login_required
def get_feeds_for_user():
    from pymongo import MongoClient
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    db = client.feeds
    collection = db.user_feeds_map
    list_of_feeds = collection.find_one({'user_name': g.user['user_email']})['listOfFeeds']
    #list_of_feeds = [
    #    {'label': u'default',
    #                    'feeds': [{'feed_label':'Hacker News', 'URI':u'https://news.ycombinator.com/rss'},
    #                              {'feed_label':'NDTV Recent', 'URI':u'http://feeds.feedburner.com/NDTV-LatestNews' }]},
    #    {'label': u'Scalability',
    #                    'feeds': [{'feed_label':'High Scalability', 'URI':u'http://highscalability.com/rss.xml'}]
    #                }]
    list_of_feeds_export = []
    for feed_label, feeds_list in list_of_feeds.iteritems():
        feed_info = {}
        feed_info['label'] = feed_label
        feed_info['feeds'] = []
        for feed in feeds_list:
            feed_info['feeds'].append({"feed_label" : db.feeds_meta.find_one({"xmlUrl":feed})['meta_info'], "URI":feed })
        list_of_feeds_export.append(feed_info)

    return json.dumps(list_of_feeds_export)

@app.route('/get_top_stories_for_user', methods=['GET'])
#@login_required
def get_top_stories_for_user():
    user_name = "udnahc"

    from pymongo import MongoClient
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    db = client.feeds
    collection = db.feeds_dump
    list_of_feeds = collection.find().sort('parsed_time', -1).limit(20)
    list_of_feeds_count = list_of_feeds.count()
    feeds_list = []
    for feeds in list_of_feeds:
        feed_info = {}
        feed_info['description'] = feeds['description']
        feed_info['link'] = feeds['link']
        feed_info['title'] = feeds['title']
        feed_info['published_entry'] = feeds['parsed_time'].strftime("%Y-%m-%d %H:%M:%S")
        feeds_list.append(feed_info)
    return json.dumps(feeds_list)

@app.route('/upload_opml_file', methods=['POST'])
def parse_opml_file():
        file = request.files['file']
        outline = opml.parse(file)
        logged_in_user_id = g.user['user_email']

        from feeds_helper import import_opml_file
        try:
            import_opml_file(logged_in_user_id, file, mongo_lib)
            return json.dumps({"message":"OPML imported successfully"})
        except Exception,e:
            return json.dumps({"message":"Could not import OPML file"})

@app.route('/get_feed_labels_for_user', methods=['GET'])
def get_feed_labels_for_user():
    feed_labels = mongo_lib.get_feed_labels_for_user(g.user['user_email'])
    print feed_labels
    return json.dumps(feed_labels)

@app.route('/fetch_feeds_for_url', methods=['POST'])
def view_feeds_for_url():
    input_dict = json.loads(request.data)
    feed_uri = input_dict['feed_uri']
    feeds_list = mongo_lib.get_entries_for_a_particular_feed(feed_uri,feed_no_limit=20)
    return json.dumps(feeds_list)


if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
