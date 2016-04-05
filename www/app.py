from flask import Flask, render_template

# get all the models Ben already described with mongoengine from baleen source
import baleen.models as db

# set up an app instance
app = Flask(__name__)
# set debug to true to get debug pages when there is an error
# app.debug = True

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

@app.route("/job_status")
def latest_job():
    # get the last job executed
    db.connect()
    latest_job = db.Job.objects.order_by('-finished').first()

    # load all data into job_status template
    return render_template('job_status.html',
                           latest_job=latest_job)

if __name__ == "__main__":
    # if you run this file as a script, it will start the flask server
    app.run(host="0.0.0.0")
