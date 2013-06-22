from feedr.feed_models import *
from datetime import datetime 
from .read_update_feed import check_and_parse_feed
import logging
import opml
logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger(__name__)

def create_entries():
    outline = opml.parse("/home/cs/Projects/hqfeed/subscriptions.xml")
    for entry in outline:
   
        if hasattr(entry, "xmlUrl"):
            f = Feeds()
            f.mongo_feed_id = entry.xmlUrl
            session.add(f)
            continue

        if hasattr(entry, '_outlines'):
            for ent in entry._outlines:
                f = Feeds()
                f.mongo_feed_id = ent.xmlUrl
                session.add(f)

    session.commit()
    print "Total feeds created ", session.query(Feeds).count()

def delete_entries():
    session.query(Feeds).delete()

def parse_feed():
    all_feeds = session.query(Feeds).all()
    for feed in all_feeds:
        logger.debug("Sending URL %s to task queue " % (feed.mongo_feed_id))
        result = check_and_parse_feed.delay(feed.mongo_feed_id)
