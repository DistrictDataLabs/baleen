from flask import Flask, render_template
import os,re,datetime


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

def get_logs(started,finished):
    infile = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','baleen.log'))
    logitems = []
    with open(infile) as f:
         for line in f.readlines():
             linedate = re.compile(r".*\[\s?(\d+/\D+?/.*?)\]").search(line).group(1)
             fdate = datetime.datetime.strptime(linedate, '%d/%b/%Y:%H:%M:%S +0000')
             if started <= fdate <= finished:
                 logitems.append(line.decode('utf-8'))
    return logitems

@app.route("/job_status")
def latest_job():
    # get the last job executed
    db.connect()
    latest_job = db.Job.objects.order_by('-finished').first()

    started = latest_job.started
    finished = latest_job.finished
    logitems = get_logs(started,finished)

    # load all data into job_status template
    return render_template('job_status.html',
                           latest_job=latest_job,
                           logitems=logitems)

if __name__ == "__main__":
    # if you run this file as a script, it will start the flask server
    app.run(host="0.0.0.0",debug = True)
