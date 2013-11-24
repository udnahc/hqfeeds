import requests
import simplejson as json

MAIN_URL = "http://127.0.0.1:5000/"

def add_rss_feed(feed_name):
    url = "%s%s" % (MAIN_URL, 'add_feed')
    requests.post(url, data=feed_name)

def subscribe_rss_feed(user_name,feed_name):
    url = "%s%s" % (MAIN_URL, 'subscribe')
    data = {'user_name': user_name, 'feed_name': feed_name}
    requests.post(url, data=json.dumps(data))


def add_tags(user_name,feed_name, tags):
    url = "%s%s" % (MAIN_URL, 'add_tag')
    data = {'user_name': user_name, 'feed_name': feed_name, 'tags':tags}
    requests.post(url, data=json.dumps(data))

def remove_tags(user_name,feed_name, tags):
    url = "%s%s" % (MAIN_URL, 'remove_tag')
    data = {'user_name': user_name, 'feed_name': feed_name, 'tags':tags}
    requests.post(url, data=json.dumps(data))

def bookmark_uri(user_name, tags, direct_uri, feed_uri):
    url = "%s%s" % (MAIN_URL, 'bookmark')
    data = {'user_name': user_name, 'feed_uri': feed_uri, 'uri': direct_uri, 'tags':tags}
    requests.post(url, data=json.dumps(data))
