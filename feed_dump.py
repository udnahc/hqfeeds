"""
This is the python program that would read the feed from time to time and dump the related feed info into the feeds_dump collection in the feeds database
"""
import pymongo
import opml
from feed_models import *
from datetime import datetime

outline = opml.parse("/jchandrashekar/Projects/hqfeeds/google-reader-subscriptions.xml")

from pymongo import MongoClient
client = MongoClient()
client = MongoClient('localhost', 27017)

db = client.feeds
collection = db.feeds_dump

urls = []

def create_entries():
    for entry in outline:
        f = Feeds(FeedUser = t)
        f.is_read = False
        f.is_starred = False
    
        if hasattr(entry, "xmlUrl"):
            f.feed_label = "hqfeed_Default"
            f.mongo_feed_id = entry.xmlUrl
            dbsession.add(f)
            urls.append(f.mongo_feed_id)
            continue

        if hasattr(entry, '_outlines'):

            f.feed_label =  entry.text
            for ent in entry._outlines:
                f.mongo_feed_id = ent.xmlUrl
                dbsession.add(f)
                urls.append(f.mongo_feed_id)

    dbsession.commit()

create_entries()
all_feeds = dbsession.query(Feeds).all()
for feed in all_feeds:
    urls.append(feed.mongo_feed_id)

import feedparser
for url in urls:
    feed_entry = {}
    feed = feedparser.parse(url)
    feed_entry['xmlUrl'] = url
    feed_entries = []
    for entry in feed['entries']:
        feed_entry['title'] = entry.title
        if hasattr(entry, 'description'):
            feed_entry['description'] = entry.description
        if hasattr(entry, 'content'):
            feed_entry['content'] = entry.content
        if hasattr(entry, 'published'):
            feed_entry['published_entry'] = entry.published
        feed_entry['link'] = entry.link
        feed_entry['parsed_time'] = datetime.now()
        collection.insert(feed_entry, manipulate=False, safe=True)

import pdb; pdb.set_trace()
