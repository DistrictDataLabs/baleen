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
import baleen

from baleen.config import settings
from baleen.models import Feed, Post, Job, Log
from baleen.utils.timez import WEB_UTC_DATETIME

from flask import Flask, render_template, request
from flask.ext.mongoengine import MongoEngine
from flask_humanize import Humanize

##########################################################################
## Flask Application
##########################################################################

# set up an app instance
app = Flask(__name__)

# set debug to true to get debug pages when there is an error
app.debug = settings.debug

# configure the app with the confire settings
app.config['MONGODB_SETTINGS'] = {
    'db':   settings.database.name,
    'host': settings.database.host,
    'port': settings.database.port,
}

# connect to the database using the Flask extension
db = MongoEngine(app)

# add the humanize extension
humanize = Humanize(app)

##########################################################################
## Routes
##########################################################################

@app.route("/")
def index():
    """
    Displays an index page with the feed listing
    """
    # get all the stuff we want
    feeds = Feed.objects()
    feed_count = feeds.count()
    topics = set([feed.category for feed in Feed.objects.only('category')])
    feeds_topics_counts = len(topics)
    feed_icons = {'gaming':'fa fa-gamepad',
                  'design':'fa fa-building-o',
                  'business':'fa fa-briefcase',
                  'cinema':'fa fa-video-camera',
                  'data-science':'fa fa-area-chart',
                  'cooking':'fa fa-cutlery',
                  'sports':'fa fa-futbol-o',
                  'books':'fa fa-book',
                  'tech':'fa fa-cogs',
                  'politics':'fa fa-university',
                  'news':'fa fa-newspaper-o',
                  'essays':'fa fa-pencil-square-o',
                  'do-it-yourself':'fa fa-wrench'
                 }
    feeds_topics = {
        topic: Feed.objects(category=topic)
        for topic in topics
    }

    # load all the data into the templates/feed_list.html template
    return render_template('index.html',
                           feeds=feeds,
                           feeds_topics=feeds_topics,
                           feed_count=feed_count,
                           topic_count=feeds_topics_counts,
                           feed_icons=feed_icons)

@app.route("/status/")
def status():
    """
    Displays the current Baleen status and job listing
    """
    version = baleen.get_version()
    counts = {
        'feeds': Feed.objects.count(),
        'posts': Post.objects.count(),
        'jobs':  Job.objects.count(),
    }
    latest_job = Job.objects.order_by('-started').first()
    latest_feed = Feed.objects.order_by('-updated').first()
    latest_post = Post.objects.order_by('-id').first()
    recent_jobs = Job.objects.order_by('-started').limit(10)

    # load all data into job_status template
    return render_template(
        'status.html',
        latest_job=latest_job,
        latest_feed=latest_feed,
        latest_post=latest_post,
        version=version,
        counts=counts,
        dtfmt=WEB_UTC_DATETIME,
        recent_jobs=recent_jobs
    )


@app.route("/logs/")
def logs():
    """
    Displays log records from the Mongo Database.
    This is paginated and allows flexible per-page counts (max 200 record).
    """
    # Get pagination information for request
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 200)

    # Compute the pagination variables
    n_logs   = Log.objects.count()
    n_pages  = (n_logs + per_page // 2) // per_page
    nextp    = page + 1 if page + 1 <= n_pages else None
    prevp    = page - 1 if page > 1 else None

    # Perform query
    offset   = (page - 1) * per_page
    logs     = Log.objects.order_by('-id').skip(offset).limit(per_page)

    return render_template(
        'logs.html',
        page = page,
        num_pages = n_pages,
        per_page  = per_page,
        logs = logs,
        num_logs = n_logs,
        next = nextp,
        prev = prevp,
    )


##########################################################################
## Main Method
##########################################################################

if __name__ == "__main__":
    # if you run this file as a script, it will start the flask server
    app.run(host=settings.server.host, port=settings.server.port)
