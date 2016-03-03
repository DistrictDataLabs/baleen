# baleen.wrangle
# Wrangles the post objects from a synchronized feed.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 21:52:49 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: wrangle.py [] benjamin@bengfort.com $

"""
Wrangles the post objects from a synchronized feed.

Feed objects don't require a lot of wrangling, and are handled primarily by
the FeedSync object. However Posts do require some hoop jumping, which this
module provides.
"""

##########################################################################
## Imports
##########################################################################

import requests

from copy import deepcopy
from dateutil import parser as dtparser

from baleen.models import Post
from baleen.utils.decorators import reraise
from baleen.exceptions import WranglingError, FetchError

##########################################################################
## Module Constants
##########################################################################

FEEDPARSER_REMOVABLE_FIELDS = (
    'id', 'published_parsed', 'expired_parsed',
    'updated', 'updated_parsed',  'created', 'created_parsed',
)

##########################################################################
## Post Wrangling Object
##########################################################################

class PostWrangler(object):
    """
    As FeedSync wraps Feed to do work, so to does PostWrangler wrap an entry
    to create a Post object, to ensure that data is of a high quality, and to
    do extra things like fetch the full webpage from the URL provided.

    This object directly converts its input (a dict) to a models.Post object.
    """

    @classmethod
    def factory(klass, entries, feed=None):
        """
        Yields a post wrangler for each entry in the entries.
        """
        for entry in entries:
            yield klass(deepcopy(entry), feed=feed)

    def __init__(self, entry, feed=None):
        """
        Entry is expected to be the dictionary object from a FeedSync
        After wrangling, it will become a models.Post object.
        """
        self.feed = feed
        self.post = entry

    def is_wrangled(self):
        """
        Checks the class of the post to see if wrangling has occurred.
        """
        return isinstance(self.post, Post)

    @reraise(klass=WranglingError)
    def wrangle(self, save=True):
        """
        Converts the raw entry to standard data. If save, saves to database.

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

            - removes the id field so a Mongo generated ObjectID is stored.

        See the models.Post for more information on the data structure.

        NOTE: This method is destructive, the raw entry will be converted.
        """
        ## Don't rewrangle an already wrangled post
        if self.is_wrangled():
            return self.post

        ## Saves typing self.post everywhere
        post = self.post.copy()

        ## Remove unwanted fields
        for field in FEEDPARSER_REMOVABLE_FIELDS:
            if field in post: del post[field]

        ## Handle the pubdate and published strings
        post['pubdate'] = dtparser.parse(post.pop('published')) if 'published' in post else None

        ## Handle the tags in the entry
        post['tags'] = [tag['term'] for tag in self.post.tags] if 'tags' in post else []

        ## Rename the link field to url
        post['url'] = self.post.link or post.get('href', None) or self.post.id
        if 'link' in post: del post['link']

        ## Handle the content
        if 'content' not in post:
            post['content'] = post.get('summary')
        else:
            selected = None
            for idx, item in enumerate(post['content']):
                if idx == 0:
                    # Take the first item
                    selected = item
                elif item['type'] == 'text/html':
                    # Unless we find another item that is html
                    selected = item

            # Update the post with the content info
            post['language'] = selected.get('language')
            post['mimetype'] = selected.get('type')
            post['content']  = selected.get('value')

        ## Create the post object
        ## Start using self.post here!
        self.post = Post(feed=self.feed, **post)
        if save:
            self.post.save()

        return self.post

    @reraise(klass=FetchError)
    def fetch(self, save=True):
        """
        Fetches the entire webpage for the post. If save, adds the page to
        the content of the post and saves it back to the database.

        Raises an exception if not wrangled yet.
        Raises exceptions if there is a problem with the fetch.
        """
        if not self.is_wrangled():
            raise ValueError("Entry not yet wrangled, cannot fetch.")

        response = requests.get(self.post.url)
        response.raise_for_status()

        if response.text:
            self.post.content = response.text

        if save:
            self.post.save()

        return self.post
