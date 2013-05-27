from flask import Flask
from flask import render_template
from flask import request
from datetime import datetime
import pymongo

app = Flask(__name__)

@app.route('/')
def index_page():
    import opml
    #outline = opml.parse("/home/arjuna/feedr/Reader/subscriptions.xml")
    outline = opml.parse("/home/cs/Projects/hqfeed/subscriptions.xml")
    return render_template('layout.html', outline=outline)


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
    app.run(host="0.0.0.0")
