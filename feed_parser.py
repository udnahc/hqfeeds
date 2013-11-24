from flask import (Flask, redirect, url_for, session, render_template, flash,
                   request, make_response, g)
from flask.ext.login import (LoginManager, login_user, logout_user, login_required,
                             current_user)
from flask.ext.oauth import OAuth
import simplejson as json
import requests
import os
import opml
import pymongo
from feed_models import Base,  FeedUser, Feeds, Tag, feeds_tags, User
from feed_models import dbsession
import feed_models as fm 
import logging

logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# import config from $APP_CONFIG file

app.config.from_envvar('APP_CONFIG')  # export APP_CONFIG=/path/to/settings.cfg
app.secret_key = app.config['SECRET_KEY']

oauth = OAuth()

# twitter oauth2 setup
twitter = oauth.remote_app('twitter',
                           base_url='https://api.twitter.com/1/',
                           request_token_url='https://api.twitter.com/oauth/request_token',
                           access_token_url='https://api.twitter.com/oauth/access_token',
                           authorize_url='https://api.twitter.com/oauth/authenticate',
                           consumer_key=app.config['TWITTER_CLIENT_ID'],
                           consumer_secret=app.config['TWITTER_CLIENT_SECRET']
                           )

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.after_request
def after_request(response):
   dbsession.remove()
   return response

#@login_required
@app.route('/', methods=['GET'])
def data_index():
    #all_feeds = fm.session.query(FeedUser,Feeds).filter(FeedUser.id == current_user.id).filter(FeedUser.id == Feeds.feed_user_id).all()
    if not g.user:
        return render_template('login.html')

    user_name = g.user.name
    from pymongo import MongoClient
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    
    db = client.feeds
    collection_of_feeds_and_tags = {}
    feed_collection = db.user_feeds_map.find_one({'user_name':user_name})['listOfFeeds']
    for tag, feeds_list in feed_collection.iteritems():
        collection_of_feeds_and_tags[tag] = {}
        for feed in feeds_list:
            title = db.feeds_meta.find_one({'xmlUrl': feed})['meta_info']
            collection_of_feeds_and_tags[tag][feed] = title
    
#---------------------------------------------------    
#     all_feeds = fm.dbsession.query(Feeds).all()
#     uniqueTags = []
#     withoutTags = []

# #    for each_feed in all_feeds:
# #        try:
#     for each_feed in all_feeds:
#         try:
#             tag =  each_feed.tags[0]
#             uniqueTags.append(tag)
#         except:
#             withoutTags.append(each_feed)
#---------------------------------------------------
#        except:
#            pass
    return json.dumps(collection_of_feeds_and_tags)

@app.route('/get_logged_in_user_info', methods=['GET'])
def get_user_info():
    if g.user:
        user_info = {'is_user_logged':True, 'logged_in_user' : g.user.name }
    else:
        user_info = {'is_user_logged': False }
    return json.dumps(user_info)

@app.route('/show_feed_entries/', methods=['POST'])
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
            entries = collection.find({"xmlUrl":url}).sort("parsed_time", pymongo.DESCENDING)
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
        return json.dumps({'login' : False })

    user = User.query.filter_by(name=resp['screen_name']).first()

    # user never signed on
    if user is None:
        user = User(resp['screen_name'])
        dbsession.add(user)

    # in any case we update the authenciation token in the db
    # In case the user temporarily revoked access we will have
    # new tokens here.
    user.oauth_token = resp['oauth_token']
    user.oauth_secret = resp['oauth_token_secret']
    dbsession.commit()

    session['user_id'] = user.id
    return json.dumps({'login': True, 'response': resp})

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

# @app.route('/login')
# def login():
#     logintype = request.args.get('logintype') or None
#     if logintype:
#         return redirect(url_for('login_'+logintype))
#     return render_template('login.html')

@app.route('/login')
def login():
    """Calling into authorize will cause the OpenID auth machinery to kick
    in.  When all worked out as expected, the remote application will
    redirect back to the callback URL provided.
    """
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))

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

# @app.route('/logout')
# def logout():
#     session.pop('user_id', None)
#     flash('You were signed out')
#     return redirect(request.referrer or url_for('thanks'))

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    return json.dumps({'status': 'done'})

@app.route('/add_feed', methods=['POST'])
def add_feed():
    uri = request.data
    from tasks.read_update_feed import check_and_parse_feed
    check_and_parse_feed(uri)
    return_dict = {uri: "created"}
    return json.dumps(return_dict)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    input_dict = json.loads(request.data)
    from pymongo import MongoClient
    client = MongoClient()
    client = MongoClient('localhost', 27017)

    db = client.feeds
    collection = db.user_feeds_map
    collection.update({'user_name':input_dict['user_name']}, {"$addToSet" : {'listOfFeeds.default' : input_dict['feed_name']}}, upsert=True)
    from tasks.read_update_feed import check_and_parse_feed
    check_and_parse_feed(input_dict['feed_name'])

    return json.dumps({"value": "created"})

@app.route('/add_tag', methods=['POST'])
def add_tag():
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
        collection.update({'user_name':input_dict['user_name']}, {"$addToSet" : {'listOfFeeds.%s' % tag : uri}}, upsert=True)
    return json.dumps({'info': 'tags_added'})

@app.route('/remove_tag', methods=['POST'])
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
        collection.update({'user_name':input_dict['user_name']}, {"$pull" : {'listOfFeeds.%s' % tag : uri}}, upsert=True)
    return json.dumps({'info': 'tags_removed'})

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0",port=5000)
