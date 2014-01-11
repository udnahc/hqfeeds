from ..feed_models import *
from datetime import datetime 
from .read_update_feed import check_and_parse_feed
import logging
import opml
logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger(__name__)

def create_entries():
    outline = opml.parse("/jchandrashekar/Projects/hqfeeds/google-reader-subscriptions.xml")
    default_tag = Tag("hqfeed_default")
    for entry in outline:
        if hasattr(entry, "xmlUrl"):
            f = Feeds()
            f.mongo_feed_id = entry.xmlUrl 
            f.feed_title = entry.title
            dbsession.add(f)
            continue
        if hasattr(entry, '_outlines'):
            for ent in entry._outlines:
                f = Feeds()
                f.mongo_feed_id = ent.xmlUrl
                f.feed_title = ent.title
                f.tags = [Tag(entry.text)]
                dbsession.add(f)
    dbsession.commit()
    print "Total feeds created ", dbsession.query(Feeds).count()

def delete_entries():
    ss = feeds_tags.delete()
    dbsession.execute(ss)
    dbsession.query(Feeds).delete()
    dbsession.query(Tag).delete()

def parse_feed():
    all_feeds = dbsession.query(Feeds).all()
    for feed in all_feeds:
        logger.debug("Sending URL %s to task queue " % (feed.mongo_feed_id))
        result = check_and_parse_feed.delay(feed.mongo_feed_id)
