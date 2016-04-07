# baleen.www.app
# Flask application definition in Baleen.
#
# Author:   Laura Lorenz <lalorenz6@gmail.com>
# Created:  Sun Apr 3 12:59:42 2016 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: app.py [] lalorenz6@gmail.com $

"""
Flask application definition in Baleen.
"""

##########################################################################
## Imports
##########################################################################

import os
import codecs
import datetime
import baleen
import baleen.models as db

from itertools import islice
from flask import Flask, render_template
from baleen.config import settings


##########################################################################
## Flask Application
##########################################################################

# set up an app instance
app = Flask(__name__)
# set debug to true to get debug pages when there is an error
app.debug = settings.debug


##########################################################################
## Routes
##########################################################################

@app.route("/")
def index():
    # connect to the database
    db.connect()
    # get all the stuff we want
    feeds = db.Feed.objects()
    feed_count = feeds.count()
    topics = set([feed.category for feed in db.Feed.objects.only('category')])
    feeds_topics_counts = len(topics)
    feeds_topics = {
        topic: db.Feed.objects(category=topic)
        for topic in topics
    }

    # load all the data into the templates/feed_list.html template
    return render_template('feed_list.html',
                           feeds=feeds,
                           feeds_topics=feeds_topics,
                           feed_count=feed_count,
                           topic_count=feeds_topics_counts)

def get_logs():
    infile = settings.logfile
    file = reversed(list(codecs.open(infile,'r',encoding='utf8')))
    logitems = islice(file,20)
    return logitems

@app.route("/status/")
def latest_job():
    # get the last job executed
    db.connect()
    version = baleen.get_version()
    counts = [db.Feed.objects.count(),db.Post.objects.count(),db.Job.objects.count()]
    latest_job = db.Job.objects.order_by('-started').first()
    latest_feed = db.Feed.objects.order_by('-updated').first()
    latest_post = db.Post.objects.order_by('-id').first()
    td = datetime.datetime.now() - latest_job.started
    running_time = str(td)
    logitems = get_logs()

    # load all data into job_status template
    return render_template('job_status.html',
                           latest_job=latest_job,
                           latest_feed=latest_feed,
                           latest_post=latest_post,
                           version=version,
                           counts=counts,
                           running_time=running_time,
                           logitems=logitems)


##########################################################################
## Main Method
##########################################################################

if __name__ == "__main__":
    # if you run this file as a script, it will start the flask server
    app.run(host=settings.server.host, port=settings.server.port)
