from flask import Flask
from flask import render_template
from flask import request

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
    if request.method == "POST":

        from pymongo import MongoClient
        client = MongoClient()
        client = MongoClient('localhost', 27017)
        
        db = client.feeds
        collection = db.feeds_dump
        url = request.form['url']

        feed_name = request.form['feed_name']
        if url:
            cur = collection.find({"xmlUrl":url})
            entries = cur.next()['feed_info']

        return render_template('feed_info.html', entries=entries, feed_name=feed_name, url=url)

@app.route('/login')
def login():
    return render_template('login.html')
    
if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")
