"""
This is the python program that would read the feed from time to time and dump the related feed info into the feeds_dump collection in the feeds database
"""
import pymongo
import opml
from feed_models import *

outline = opml.parse("/home/arjuna/feedr/Reader/subscriptions.xml")

from pymongo import MongoClient
client = MongoClient()
client = MongoClient('localhost', 27017)

db = client.feeds
collection = db.feeds_dump

urls = []

for entry in outline:
    f = Feeds(FeedUser = t)
    f.is_read = False
    f.is_starred = False

    if hasattr(entry, "xmlUrl"):
        f.feed_label = "hqfeed_Default"
        f.mongo_feed_id = entry.xmlUrl
        session.add(f)
        urls.append(f.mongo_feed_id)
        continue

    if hasattr(entry, '_outlines'):
        f.feed_label =  entry.text
        for ent in entry._outlines:
            f.mongo_feed_id = ent.xmlUrl
            session.add(f)
            urls.append(f.mongo_feed_id)

session.commit()

import feedparser
#urls = ["http://tambrahmrage.tumblr.com/rss"]

for url in urls:
    feed_entry = {}
    feed = feedparser.parse(url)
    feed_entry['xmlUrl'] = url
    feed_entries = []
    for entry in feed['entries']:
        feed_info = {}
        feed_entry['feed_info'] = []
        feed_info['title'] = entry.title
        if hasattr(entry, 'description'):
            feed_info['description'] = entry.description
        if hasattr(entry, 'content'):
            feed_entry['content'] = entry.content
        if hasattr(entry, 'published'):
            feed_info['published_entry'] = entry.published
        feed_entries.append(feed_info) 

    feed_entry['feed_info'] = feed_entries
    print feed_entry,'\n'
    collection.insert(feed_entry, upsert=True,safe=True)
print "done"