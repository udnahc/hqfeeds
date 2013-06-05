from flask import (Flask, redirect, url_for, session, render_template,
                   request, make_response)
from flask.ext.login import (LoginManager, login_user, logout_user, login_required,
                             current_user)
from flask.ext.oauth import OAuth
from json import dumps, loads
import requests
import os
import opml
import pymongo
from feed_models import Base, Anonymous, FeedUser, Feeds, Tag
import feed_models as fm 

app = Flask(__name__)

# import config from $APP_CONFIG file

app.config.from_envvar('APP_CONFIG')  # export APP_CONFIG=/path/to/settings.cfg
app.secret_key = app.config['SECRET_KEY']

oauth = OAuth()
# google oauth2 setup
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params= {'scope': 'https://www.googleapis.com/auth/userinfo.email \
                          https://www.googleapis.com/auth/userinfo.profile  http://www.google.com/reader/api/0/subscription/list',
                                                 'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
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
# login manager

login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'
login_manager.anonymous_user = Anonymous

@login_manager.user_loader
def load_user(user_id):
    return FeedUser.load(user_id)
    

@app.route('/')
def index():
    # return current_user.name,subs #
    subs = request.args.getlist('subs') or None
    return render_template('subs.html',subs=subs)

@app.route('/login_google')
def login_google():
    # session['next'] = request.args.get('next') or request.referrer or None
    session['next'] = None
    callback=url_for('google_callback', _external=True)    
    return google.authorize(callback=callback)

@app.route('/login_twitter')
def login_twitter():
    # session['next'] = request.args.get('next') or request.referrer or None
    session['next'] = None    
    callback=url_for('twitter_callback')    
    return twitter.authorize(callback=callback)
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route(app.config['REDIRECT_URI'])
@google.authorized_handler
def google_callback(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    if access_token:
        r = requests.get('https://www.googleapis.com/oauth2/v1/userinfo',
                         headers={'Authorization': 'OAuth ' + access_token})

        subscriptions = requests.get('http://www.google.com/reader/api/0/subscription/list?output=json',
                                     headers={'Authorization': 'OAuth ' + access_token})

        import pprint;pprint.pprint(subscriptions)

        if r.ok:
            data = loads(r.text)
            oauth_id = data['id']
            user = FeedUser.load(oauth_id) or FeedUser.add(**data)
            login_user(user)
            if subscriptions.ok:
                # outline = opml.parse(subscriptions.text)
                urls = create_entries(subscriptions.json['subscriptions'],user)
                next_url = session.get('next') or url_for('index', subs=urls)
            else:
                next_url = session.get('next') or url_for('index')
            return redirect(next_url)
    return redirect(url_for('login')) 


def create_entries(outline=None,user=''):
    urls = []
    tags = [entry['categories'][0]['label'] for entry in outline]
    tags = list(set(tags))
    tagObjs = [Tag(tag) for tag in tags]
    fm.session.add_all(tagObjs)
    fm.session.commit()
    tagsMapping = [{tagObj.id:[tagObj.tag,tagObj]} for tagObj in tagObjs]

    for entry in outline:
        if 'htmlUrl' in entry:
            f = Feeds(FeedUser=user)
            f.is_read = False
            f.is_starred = False
            f.tags = [tagsMap.values()[0][1] for tagsMap in tagsMapping if tagsMap.values()[0][0] == entry['categories'][0]['label']]
            f.mongo_feed_id = entry['htmlUrl'] or 'asd'
            fm.session.add(f)
            urls.append(f.mongo_feed_id)

    fm.session.commit()

    all_feeds = fm.session.query(Feeds).all()
    for feed in all_feeds:
        urls.append(feed.mongo_feed_id)

    # import feedparser
    # for url in urls[:10]:
    #     feed_entry = {}
    #     feed = feedparser.parse(url)
    #     feed_entry['htmlUrl'] = url
    #     feed_entries = []
    #     if  feed.get('entries'):
    #         import ipdb; ipdb.set_trace()        

    #     for entry in feed['entries']:
    #         feed_entry['title'] = entry.title
    #         if hasattr(entry, 'description'):
    #             feed_entry['description'] = entry.description
    #         if hasattr(entry, 'content'):
    #             feed_entry['content'] = entry.content
    #         if hasattr(entry, 'published'):
    #             feed_entry['published_entry'] = entry.published
    #         feed_entry['link'] = entry.link
    #         feed_entry['parsed_time'] = datetime.now()
    #         collection.insert(feed_entry, manipulate=False, safe=True)
    return urls
    
@app.route(app.config['TWITTER_REDIRECT_URI'])
@twitter.authorized_handler
def twitter_callback(resp):
    access_token = resp['oauth_token']
    access_token_secret = resp['oauth_token_secret']
    session['access_token'] = access_token, ''
    if access_token:
        oauth_id = resp['user_id']
        user = FeedUser.load(oauth_id) or FeedUser.add(**resp)
        login_user(user)
        next_url = session.get('next') or url_for('index')
        return redirect(next_url)
    return redirect(url_for('login')) 
    
@google.tokengetter
def get_access_token():
    return session.get('access_token')

@twitter.tokengetter
def get_twitter_access_token():
    return session.get('access_token')
    
# @app.route('/')
# def index_page():
#     import opml
#     #outline = opml.parse("/home/arjuna/feedr/Reader/subscriptions.xml")
#     outline = opml.parse("/home/cs/Projects/hqfeed/subscriptions.xml")
#     return render_template('layout.html', outline=outline)


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

@app.route('/login')
def login():
    logintype = request.args.get('logintype') or None
    if logintype:
        return redirect(url_for('login_'+logintype))
    return render_template('login.html')

@app.route("/like/", methods=['POST'])
def like():
    if request.method == 'POST':
        return "abc"

@app.route("/later", methods=['POST'])
def read_later():
    if request.method == 'POST':
        import pdb; pdb.set_trace()

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0",port=3333)
