from __future__ import absolute_import
from .celery import celery
from pymongo import MongoClient
import feedparser
from datetime import datetime
import logging
import simplejson as json

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

root_logger = logging.getLogger("MainProcess")
root_logger.setLevel(logging.INFO)

client = MongoClient()
client = MongoClient('localhost', 27017)

db = client.feeds
collection = db.feeds_dump
collection_title = db.feeds_meta

def sanitize_content(description):
    import lxml.html
    html = lxml.html.fromstring(description)
    for tag in html.xpath('//*[@class]'):
        tag.attrib.pop('class')
    for tag in html.xpath('//*[@style]'):
        tag.attrib.pop('style')
    return lxml.html.tostring(html)

@celery.task
def check_and_parse_feed(url):
    logger.debug("Parsing feed %s " % (url))
    feed_entry = {}
    feed = feedparser.parse(url)
    feed_entry['xmlUrl'] = url

    feed_entries = []
    for entry in feed['entries']:
        feed_entry['title'] = entry.title
        if hasattr(entry, 'description'):
            feed_entry['description'] = sanitize_content(entry.description)
        if hasattr(entry, 'content'):
            feed_entry['content'] = sanitize_content(entry.content)
        if hasattr(entry, 'published'):
            feed_entry['published_entry'] = entry.published
        feed_entry['link'] = entry.link
        if  collection.find({"link":entry.link}).count():
            logger.debug( "Link is already present skipping %s " % entry.link)
            continue
        feed_entry['parsed_time'] = datetime.now()
        collection.insert(feed_entry, manipulate=False, safe=True)
        collection_title.update({"xmlUrl":url}, {'$set': {'meta_info': feed.feed.title}}, upsert=True)

        logger.debug("Inserted link %s " % entry.link)
    logger.info("Done with  %s" % url)
