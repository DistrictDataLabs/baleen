# baleen.feed
# Handles the ingestion of documents from an RSS feed
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Sep 21 09:58:44 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: feed.py [] benjamin@bengfort.com $

"""
Handles the ingestion of documents from a list of RSS feeds.

This module provides two mechanisms for downloading a list of RSS feeds-
one that accepts as input an OPML file and then downloads all of the RSS
directly to disk. The other that uses data that is stored in Mongo to
fetch the feeds and then saves the documents to a Mongo collection.
"""

##########################################################################
## Imports
##########################################################################

import requests
import feedparser
import baleen.models as db

from copy import copy
from baleen.opml import OPML
from collections import Counter
from baleen.config import settings
from baleen.utils.timez import localnow
from baleen.utils.logger import IngestLogger
from dateutil import parser as dtparser

##########################################################################
## FeedIngestor Base
##########################################################################

class FeedIngestor(object):
    """
    The base class for any FeedIngestor.
    """

    feed_urls = None

    def get_feed_urls(self):
        """
        Should yield a list of feeds that should go out and be fetched.
        """
        if self.feed_urls:
            for url in self.feed_urls:
                yield url
        else:
            raise NotImplementedError((
                "Subclasses must either provide a list of "
                "feed_urls or override get_feed_urls."
            ))

    def feeds(self):
        """
        Returns the feedparser feed for each url in the ingestor.
        """
        for url in self.get_feed_urls():
            yield feedparser.parse(url)

    def posts(self):
        """
        An iterable that uses the list of feeds to fetch posts.
        """
        for feed in self.feeds():
            for entry in feed.entries:
                yield self.wrangle(entry)

    def wrangle(self, entry):
        """
        Handles each entry from the feed and converts to standard data.
        Metholodolgy of wrangling is as follows:

            - all fields are kept in the entry except `published` and
              `published_parsed` since these many not contain TZ data -
              instead these two fields are replaced by `pubdate`. If there
              is no publication date, `pubdate` is set to None.

            - the tags field, if it exists, is converted to a list of
              strings. Although this may cause some data loss; it will
              make tagging of all posts simpler for the application.

            - link will be renamed url

            - content will be populated with summary, if content does not
              exist in the feed. Supposedly feedparser was already doing
              this, but it appears to not be regular.

            - title, url, content, and tags will all be encoded UTF-8.

        All of the rest of the fields will be retained after these changes
        for subclasses to do with as they please. See the models.Post for
        more information on the standard data structure.
        """
        post = entry.copy()

        ## Handle the pubdate and published strings
        if 'published_parsed' in post: del post['published_parsed']
        post['pubdate'] = dtparser.parse(post.pop('published')) if 'published' in post else None

        ## Handle the updated parsed string
        if 'updated' in post: del post['updated']
        if 'created' in post: del post['created']
        if 'updated_parsed' in post: del post['updated_parsed']
        if 'created_parsed' in post: del post['created_parsed']
        if 'expired_parsed' in post: del post['created_parsed']

        ## Handle the tags in the entry
        post['tags'] = [tag['term'] for tag in entry.tags] if 'tags' in entry else []

        ## Rename the link field to url
        post['url']  = entry.link or post.get('href', None) or entry.id
        if 'link' in post: del post['link']

        ## Handle the content
        if 'content' not in post:
            post['content'] = entry.get('summary')
        else:
            selected = None
            for idx, item in enumerate(entry['content']):
                if idx == 0:
                    # Take the first item
                    selected = item
                elif item['type'] == 'text/html':
                    # Unless we find another item that is html
                    selected = item
            post['language'] = selected.get('language')
            post['mimetype'] = selected.get('type')
            post['content']  = selected.get('value')

        ## Fetch the content if requested.
        if settings.fetch_html:
            page = self.fetch(post.get('url'))
            if page:
                post['content'] = page

        return post

    def fetch(self, url):
        """
        Fetches the given url and returns the content, capturing errors.
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                self.logger.error(
                    "Could not fetch '{}': {} {}".format(
                        url, response.status_code, response.reason
                    )
                )
        except Exception as e:
            self.logger.error(
                "Could not fetch '{}': {}".format(
                    url, str(e)
                )
            )

    def fields(self):
        """
        Returns a count of all the available fields in every entry.
        """
        meta = Counter()
        flds = Counter()

        for feed in self.feeds():
            feed = feedparser.parse(feed['link'])

            meta[feed.version] += 1
            meta['feeds'] += 1

            for entry in feed.entries:
                meta['entries'] += 1
                for key in entry.keys():
                    flds[key] += 1

        meta = dict(meta)
        meta['fields'] = dict(flds)
        return meta

    def ingest(self):
        """
        Intended as the entry point for ingestion
        """
        raise NotImplementedError("Subclasses must implement")

    def __len__(self):
        return sum(1 for feed in self.feeds())

##########################################################################
## MongoFeedIngestor
##########################################################################

class MongoFeedIngestor(FeedIngestor):
    """
    Uses the Mongo feed collection to go out and ingest posts.
    """

    def __init__(self, **kwargs):
        self.logger = kwargs.get('logger', IngestLogger())
        self.status = "PENDING"
        self.current_feed = None
        self.counts = None

    def get_feed_urls(self):
        """
        Accesses the feed collection for the list of feeds.

        NOTE: You must connect to the MongoDB before calling this method!
        """
        for feed in db.Feed.objects(active=True).only('link'):
            yield feed.link

    def update_feed(self, feed, result):
        """
        Updates a feed with information from the feedparser result.
        """
        feed.fetched = localnow()
        if 'etag' in result:     feed.etag     = result.etag
        if 'modified' in result: feed.modified = result.modified
        if 'version' in result:  feed.version  = result.version
        if 'href' in result:     feed.link     = result.href

        for key, value in result.feed.items():
            if key in ('updated', 'updated_parsed', 'id',
                       'published', 'published_parsed', 'category'):
                # Ignore these generated or protected fields
                continue

            elif key == 'link':
                feed.urls['htmlurl'] = value

            elif key == 'links':
                for idx, link in enumerate(value):
                    if 'rel' in link:
                        feed.urls[link['rel'] + str(idx)] = link['href']
                    else:
                        feed.urls["link%i" % idx] = link['href']
            else:
                setattr(feed, key, value)

        return feed

    def feeds(self, save=True):
        """
        Returns the feedparser feed for each url in the ingestor.
        """
        for url in self.get_feed_urls():
            try:
                feed   = db.Feed.objects.get(link=url)
                result = feedparser.parse(url, etag=feed.etag, modified=feed.modified)
                if not result.entries:
                    # Nothing returned, continue
                    self.logger.warning("No entries available for feed %s (%s)" %
                                        (feed.title, feed.id))
                    continue

                # Update feed properties
                feed = self.update_feed(feed, result)
                self.current_feed = feed

                if save: feed.save()
                self.counts['feeds'] += 1

                yield result
            except Exception as e:
                self.logger.error("Feed Error for feed %s (%s): %s" % (feed.title, feed.id, str(e)))
                self.counts['errors'] += 1
                continue

    def posts(self, save=True):
        """
        For every post that is fetched by super, yields the models.Post
        """
        for idx, post in enumerate(super(MongoFeedIngestor, self).posts()):
            try:
                post = db.Post(feed=self.current_feed, **post)

                if save: post.save()
                self.counts['entries'] += 1

                yield post
            except Exception as e:
                self.logger.error("Post Error for feed %s (%s) on entry %i: %s"
                    % (self.current_feed.title, self.current_feed.id, idx, str(e)))
                self.counts['errors'] += 1
                continue

    def wrangle(self, entry):
        """
        Performs same work as super, but also removes the id field so that
        a Mongo generated ObjectID can be stored as the id.
        """
        entry = super(MongoFeedIngestor, self).wrangle(entry)
        if 'id' in entry: del entry['id']
        return entry

    def ingest(self, verbose=True):
        """
        Entry point to ingestion
        """
        self.logger.info("Starting Ingest of Feeds from Mongo to Posts in Mongo")
        self.status = "INGESTING"
        self.counts = Counter()

        for post in self.posts():
            if verbose:
                print post

        self.status  = "FINISHED"
        msg = "Finished Ingest: %(feeds)i feeds, %(entries)i entries, %(errors)i errors"
        msg = msg % self.counts
        self.logger.info(msg)
        if verbose: print msg


    def __len__(self):
        return db.Feed.objects.count()

##########################################################################
## OPMLFeedIngestor
##########################################################################

class OPMLFeedIngestor(FeedIngestor):
    """
    Uses an OPML file to go out and ingest posts
    """

    def __init__(self, path):
        self.opml = OPML(path)

    def get_feed_urls(self):
        for feed in self.opml:
            yield feed['xmlUrl']

    def __len__(self):
        return len(self.opml)

if __name__ == '__main__':
    db.connect()
    ingestor = MongoFeedIngestor()
    # ingestor = OPMLFeedIngestor('fixtures/feedly.opml')
    ingestor.ingest()
