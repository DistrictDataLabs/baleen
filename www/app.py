from flask import Flask, render_template
import os,codecs
from itertools import islice
import baleen

# get all the models Ben already described with mongoengine from baleen source
import baleen.models as db

# set up an app instance
app = Flask(__name__)
# set debug to true to get debug pages when there is an error
app.debug = True

@app.route("/")
def index():
    # connect to the database
    db.connect()
    # get all the stuff we want
    feeds = db.Feed.objects()
    feed_count = feeds.count()
    feeds_topics = set([feed.category for feed in feeds])
    feeds_topics_counts = len(feeds_topics)

    # load all the data into the templates/feed_list.html template
    return render_template('feed_list.html',
                           feeds=feeds,
                           feeds_topics=feeds_topics,
                           feed_count=feed_count,
                           topic_count=feeds_topics_counts)

def get_logs():
    infile = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','baleen.log'))
    with codecs.open(infile,'r',encoding='utf8') as f:
        logitems = list(islice(f,20))
    return logitems

@app.route("/job_status")
def latest_job():
    # get the last job executed
    db.connect()
    version = baleen.get_version()
    counts = [db.Feed.objects.count(),db.Post.objects.count(),db.Job.objects.count()]
    latest_job = db.Job.objects.order_by('-started').first()
    latest_feed = db.Feed.objects.order_by('-updated').first()
    latest_post = db.Post.objects.order_by('-id').first()
    logitems = get_logs()

    # load all data into job_status template
    return render_template('job_status.html',
                           latest_job=latest_job,
                           latest_feed=latest_feed,
                           latest_post=latest_post,
                           version=version,
                           counts=counts,
                           logitems=logitems)

if __name__ == "__main__":
    # if you run this file as a script, it will start the flask server
    app.run(host="0.0.0.0")
