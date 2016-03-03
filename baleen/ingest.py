# baleen.ingest
# The ingestion runner that implements ingestion for a collection of feeds.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 23:23:06 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: ingest.py [] benjamin@bengfort.com $

"""
The ingestion runner that implements ingestion for a collection of feeds.
"""

##########################################################################
## Imports
##########################################################################

import uuid

from baleen.opml import OPML
from baleen.exceptions import *
from baleen import models as db
from baleen.feed import FeedSync
from baleen.config import settings
from baleen.utils.timez import Timer
from baleen.wrangle import PostWrangler
from baleen.utils.logger import LoggingMixin
from baleen.utils.decorators import memoized

from datetime import datetime
from collections import Counter


##########################################################################
## Helper Functions
##########################################################################

def stype(obj):
    """
    Returns the string of the type. Used to count exception types.
    """
    if isinstance(obj, BaleenError):
        if hasattr(obj, "original"):
            return "{} ({})".format(
                type(obj).__name__, type(obj.original).__name__
            )
    return type(obj).__name__


##########################################################################
## Base Ingestion Class
##########################################################################

class Ingestor(LoggingMixin):
    """
    Base class for the ingestors.

    Ingestors manage the synchronization of feeds, wrangling of posts, and
    fetching of web pages to store to the Mongo database. Ingestors can
    either get feeds from a list of strings, an OPML file or a Mongo query.

    Ingestors also perform logging and exception handling.
    """

    def __init__(self, feeds=None, **options):
        self.timer   = None         # Processing timer
        self.jobid   = None         # Unique job id for every run
        self.options = options      # Any other options passed in
        self._feeds  = feeds        # Allows pass in feed collection
        self.errors  = Counter()    # Count the number of error types

    @property
    def name(self):
        return self.__class__.__name__

    @memoized
    def counts(self):
        """
        Keep track of counts and ensure zero keys exist.
        """
        counts = Counter()
        for key in ('feeds', 'posts', 'errors', 'feed_error'):
            counts[key] = 0
        return counts

    def feeds(self):
        """
        This is the primary entry point for subclasses, they must specificy
        how to get access to a collection of feeds to syncrhonize.
        """
        if self._feeds is not None:
            return self._feeds

        raise IngestionError(
            "No feeds specified for {} ingestion!".format(self.name)
        )

    def started(self):
        """
        Run when the ingestor is started and used for logging. Subclasses can
        use it as a hook to perform extra work right before kick off.
        """
        message = "{} job {} started".format(self.name, self.jobid)
        self.logger.info(message)

    def failed(self, exception):
        """
        Executed when a complete ingestion run has failed (very bad). Used
        to log the exception or clean up before Baleen crashes!
        """
        message = "{} job {} failed!".format(self.name, self.jobid)
        self.logger.error("Ingestion Error: {}".format(exception))
        self.logger.critical(message)

    def finished(self):
        """
        Run when the ingestor has finished and used for logging. Subclasses
        can use it as a hook to perform any completion work.
        """
        # Notify the results
        results = (
            "Processed {feeds} feeds ({timer}) "
            "{posts} posts with {errors} errors"
        ).format(
            timer=self.timer, **self.counts
        )
        self.logger.info(results)

        # Notify job finished
        message  = "{} job {} finished".format(self.name, self.jobid)
        self.logger.info(message)

    def process(self):
        """
        Runs the ingestion process by iterating over the feeds, synchronizing
        and then wrangling posts into the database as well as fetching pages.
        """
        for idx, fsync in enumerate(FeedSync.factory(self.feeds())):
            try:
                self.process_feed(fsync)
                self.counts['feeds'] += 1
            except SynchronizationError as e:
                self.counts['feed_error'] += 1
                self.errors[stype(e)] += 1
                self.logger.error(
                    u"Error on Feed {} ({}): {}".format(
                        idx+1, fsync.feed, unicode(e)
                    )
                )

    def process_feed(self, fsync):
        """
        Synchronizes a feed and catches exceptions
        """
        factory = PostWrangler.factory(fsync.entries(), fsync.feed)
        for idx, post in enumerate(factory):
            try:
                self.process_post(post)
                self.counts["posts"] += 1
            except WranglingError as e:
                self.counts["errors"] += 1
                self.errors[stype(e)] += 1
                self.logger.error(
                    u"Post Error for feed {} on entry {}: {}".format(
                        fsync.feed, idx, unicode(e)
                    )
                )

    def process_post(self, post):
        """
        Wrangles a post from a single feed and catches exceptions
        """
        post.wrangle()
        if settings.fetch_html:
            try:
                post.fetch()
            except FetchError as e:
                self.counts["fetch_error"] += 1
                self.errors[stype(e)] += 1
                self.logger.error(
                    u"Fetch Error for post \"{}\" ({}): {}".format(
                        post.post.title, post.post.url, unicode(e)
                    )
                )

    def ingest(self):
        """
        Subclasses do not typically override the ingest method. Instead they
        will override the process hooks for start, failed, and finish,  or the
        process method directly.
        """
        # Set a unique job id for every time run is called.
        # The job id is based on the hostname and a time sequence.
        self.jobid = uuid.uuid1()

        # Call the started hook for logging and notification.
        self.started()

        # Time how long it takes to perform the processing
        with Timer() as self.timer:
            try:
                self.process()
            except Exception as e:
                # If something goes wrong, call the failed hook, then raise.
                self.failed(e)
                raise

        # Call the finished hook for logging and notification.
        self.finished()


##########################################################################
## Mongo Ingestion Class
##########################################################################

class MongoIngestor(Ingestor):
    """
    Ingests feeds that are stored in the database.
    This type of ingestor also tracks information into the database.
    """

    def feeds(self):
        """
        Returns an iterator of all active feeds from the database
        """
        for feed in db.Feed.objects(active=True):
            yield feed

    def started(self):
        """
        Save a record about the job start to the database.
        """
        super(MongoIngestor, self).started()
        self.job = db.Job(jobid=self.jobid, name=self.name)
        self.job.save()

    def failed(self, exception):
        """
        Save information about the failure to the database.
        """
        super(MongoIngestor, self).failed(exception)
        self.job.failed = True
        self.job.reason = unicode(exception)
        self.job.finished = datetime.now()
        self.job.save()

    def finished(self):
        """
        Update the job record in the database.
        """
        super(MongoIngestor, self).finished()
        self.job.reason = u"OK"
        self.job.finished = datetime.now()
        self.job.counts = self.counts
        self.job.errors = self.errors
        self.job.totals = {
            "feeds": db.Feed.objects.count(),
            "posts": db.Post.objects.count(),
            "jobs": db.Job.objects.count(),
        }
        self.job.save()

##########################################################################
## OPML Ingestion Class
##########################################################################

class OPMLIngestor(Ingestor):
    """
    Ingests feeds from an OPML file.
    """

    def __init__(self, path, **options):
        self.opml = OPML(path)
        super(OPMLIngestor, self).__init__(**options)

    def feeds(self):
        """
        Returns an iterator of all active feeds from the database
        """
        for feed in self.opml:
            yield feed
