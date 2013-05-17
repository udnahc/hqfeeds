from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route('/')
def index_page():
    import opml
    outline = opml.parse("/home/arjuna/feedr/Reader/subscriptions.xml")
    #outline = opml.parse("http://www.balsamiq.com/files/BalsamiqFireHose.opml")
    return render_template('layout.html', outline=outline)


@app.route('/show_feed_entries/', methods=['POST'])
def feed_entries():
    import feedparser
    feed = None
    feed_name = None
    if request.method == "POST":
        url = request.form['url']
        feed_name = request.form['feed_name']
        if url:
            feed = feedparser.parse(url)
    return render_template('feed_info.html', feed=feed, feed_name=feed_name)

@app.route('/login')
def login():
    return render_template('login.html')
    
if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")
