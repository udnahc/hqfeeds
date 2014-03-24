__author__ = 'jchandrashekar'

def add_feed_to_feeds_meta(mongo_lib, feed_uri, feed_title):
    mongo_lib.add_feed_to_feeds_meta(feed_uri, feed_title)

def associate_tags_to_user_feed(mongo_lib,logged_in_user, tags, feed_uri):
    mongo_lib.associate_tags_to_user_feed(tags, feed_uri, logged_in_user)

def import_opml_file(logged_in_user, opml_file, mongo_lib):
    import opml
    default_tag = "default"
    outline = opml.parse(opml_file)
    for entry in outline:
        if hasattr(entry, "xmlUrl"):
            # This does not have any tags so default is the default tag
            add_feed_to_feeds_meta(mongo_lib,entry.xmlUrl, entry.title)
            associate_tags_to_user_feed(mongo_lib,logged_in_user, ['default'], entry.xmlUrl)
        if hasattr(entry, '_outlines'):
            for ent in entry._outlines:
                add_feed_to_feeds_meta(mongo_lib,ent.xmlUrl, ent.title)
                #f.tags = [Tag(entry.text)]
                associate_tags_to_user_feed(mongo_lib,logged_in_user, [entry.text], ent.xmlUrl)


def export_opml_file(logged_in_user):
    pass