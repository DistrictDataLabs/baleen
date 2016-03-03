# baleen.feed
# Handles the synchronization of an RSS feed.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Sep 21 09:58:44 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: feed.py [] benjamin@bengfort.com $

"""
Handles the synchronization of documents from an RSS feeds.
"""

##########################################################################
## Imports
##########################################################################

import feedparser

from baleen.models import Feed
from baleen.utils.timez import localnow
from baleen.exceptions import FeedTypeError
from baleen.exceptions import SynchronizationError
from baleen.utils.decorators import memoized, reraise


##########################################################################
## Module Constants
##########################################################################

FEEDPARSER_IGNORABLE_FIELDS = {
    'updated', 'updated_parsed', 'id',
    'published', 'published_parsed', 'category',
}


##########################################################################
## Feed Synchronization
##########################################################################

class FeedSync(object):
    """
    A utility that wraps both a Feed object and the feedparser library.
    The feed that is passed into the FeedSync can be one of the following:

        - a string representing the url to the RSS feed
        - a dictionary with an xmlUrl key (from OPML)
        - a Feed object loaded from MongoDB.

    The feed synchronization utility is smart enough to access what it needs.
    """

    URL   = "FEED_URL"
    DICT  = "FEED_DICT"
    MODEL = "FEED_MODEL"

    @classmethod
    def factory(klass, feeds):
        """
        Yields a feed synchronizer for each feed in the feeds.
        """
        for feed in feeds:
            yield klass(feed)

    def __init__(self, feed):
        """
        Feed can be a string (url), a dictionary with an `xmlUrl` or a Feed.
        """
        self.feed = feed

    @memoized
    def type(self):
        """
        Returns the type of the feed.
        """
        if isinstance(self.feed, basestring):
            return self.URL

        if isinstance(self.feed, Feed):
            return self.MODEL

        if isinstance(self.feed, dict):
            if not 'xmlUrl' in self.feed:
                raise FeedTypeError(
                    "Dictionary object does not contain 'xmlUrl' key!"
                )
            return self.DICT

        raise FeedTypeError(
            "Could not determine feed type from '{}'".format(type(self.feed))
        )

    @memoized
    def url(self):
        """
        Extracts the url from the feed based on the type.
        """
        return {
            self.URL: lambda: self.feed,
            self.DICT: lambda: self.feed.get('xmlUrl', None),
            self.MODEL: lambda: self.feed.link,
        }[self.type]()

    def parse(self):
        """
        Wraps the feedparser.parse function such that if the feed is an model,
        it uses the etag or modified to prevent duplicating the download.

        NOTE: Calling this function will NOT update the feed use sync instead!
        NOTE: Exceptions in this function will not be handled by Baleen!
        """
        # Only models contain the etag/modified saved information.
        if self.type == self.MODEL:
            # If there is an etag use it (even if there is also modified)
            if self.feed.etag:
                return feedparser.parse(self.url, etag=self.feed.etag)

            # If there is a modified date, then use it
            if self.feed.modified:
                return feedparser.parse(self.url, modified=self.feed.modified)

        # Otherwise just return the parse of the URL
        return feedparser.parse(self.url)

    @reraise(klass=SynchronizationError)
    def sync(self, save=True):
        """
        Calls the feedparser.parse function correctly but also synchronizes
        the state of the feed (e.g. last modified, etag, etc.) to MongoDB.

        Note: If the feed isn't a model, it just does the same as parse.

        If save is True (default) will save the Feed back to MongoDB.
        """
        # Get the result from the parse function.
        result = self.parse()

        # If this is not a model, bail out and return the result.
        if not self.type == self.MODEL:
            return result

        # Otherwise update the model in MongoDB with synchronization info.
        # Set the last fetched timestamp on the model.
        self.feed.fetched = localnow()

        # Update the feed properties from the result.
        for key in ('etag', 'modified', 'version'):
            if key in result and getattr(result, key):
                setattr(self.feed, key, getattr(result, key))

        # Update the link via the href
        if 'href' in result and result.href:
            self.feed.link = result.href

        # Update the feed items from the result.
        for key, val in result.feed.items():
            if key in FEEDPARSER_IGNORABLE_FIELDS:
                # Ignore these generated or protected fields.
                continue

            if key == 'link':
                self.feed.urls['htmlUrl'] = val

            elif key == 'links':
                for idx, link in enumerate(val):
                    if 'rel' in link:
                        self.feed.urls[link['rel'] + str(idx)] = link['href']
                    else:
                        self.feed.urls["link{}".format(idx)] = link['href']

            else:
                setattr(self.feed, key, val)

        if save:
            self.feed.save()

        return result

    def entries(self, save=True):
        """
        A helper function to simultaneously call sync and iterate over the
        entries from the feed. This is the usual method of interacting with
        the feed sync object. Note that this just returns raw dicts not Posts.
        """
        result = self.sync(save=save)
        return result.entries
