# tests.test_feed
# Test the feed module - the main entry point to Baleen
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Feb 21 15:49:18 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_feed.py [2988c53] benjamin@bengfort.com $

"""
Test the feed module - the main entry point to Baleen
"""

##########################################################################
## Imports
##########################################################################

import os
import pickle
import unittest

from mongomock import MongoClient as MockMongoClient

try:
    from unittest import mock
except ImportError:
    import mock

from baleen.feed import *
from baleen.models import *
from baleen.exceptions import FeedTypeError

##########################################################################
## Fixtures
##########################################################################

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
FEEDLY   = os.path.join(FIXTURES, "feedly.opml")
RESULT   = os.path.join(FIXTURES, "feedparser_result.pickle")

# Feed Fixtures
STR_FEED     = 'http://freakonomics.blogs.nytimes.com/feed/'
UNICODE_FEED = u'http://blog.kaggle.com/feed/'
OPML_FEED    = {
    "type":"rss", "text":"The Daily Notebook", "title":"The Daily Notebook",
    "xmlUrl":"https://mubi.com/notebook/posts.atom", "htmlUrl":"https://mubi.com/notebook/posts",
}
MONGO_FEED   = Feed(
    title = u'The Rumpus.net',
    link = u'http://therumpus.net/feed/',
    urls = {u'htmlurl': u'http://therumpus.net'},
    category = u'books',
    signature = '27c019245edb10ac1e8b8800aaeb16b3e9ddd361a7550e089398128f9f87c2ff',

)

##########################################################################
## Feed Synchronization Tests
##########################################################################

class FeedSyncTests(unittest.TestCase):

    def setUp(self):
        """
        Create the mongomock connection
        """
        self.conn = connect(host='mongomock://localhost')
        assert isinstance(self.conn, MockMongoClient)

        # Clear out the database
        for feed in Feed.objects(): feed.delete()
        for post in Post.objects(): post.delete()

    def tearDown(self):
        """
        Drop the mongomock connection
        """
        assert isinstance(self.conn, MockMongoClient)
        self.conn = None

    def test_fsync_factory(self):
        """
        Test multiple types in the feed sync factory
        """
        cases = (
            STR_FEED, UNICODE_FEED, OPML_FEED, MONGO_FEED
        )

        for fsync in FeedSync.factory(cases):
            self.assertIsInstance(fsync, FeedSync)

    def test_type_check(self):
        """
        Assert that strings, Feeds, and dicts can be sync'd
        """
        cases = (
            (STR_FEED, FeedSync.URL),
            (UNICODE_FEED, FeedSync.URL),
            (OPML_FEED, FeedSync.DICT),
            (MONGO_FEED, FeedSync.MODEL),
        )

        for feed, ftype in cases:
            fsync = FeedSync(feed)
            self.assertEqual(fsync.type, ftype)

    def test_bad_type(self):
        """
        Test that bad types raise an exception in sync
        """
        cases = (
            10, {u'htmlurl': u'https://mubi.com/notebook/posts'}, ['a','b','c']
        )

        for case in cases:
            fsync = FeedSync(case)
            with self.assertRaises(FeedTypeError):
                fsync.type

    def test_url_extraction(self):
        """
        Test the feed sync multiple type url extraction
        """
        cases = (
            (STR_FEED, STR_FEED),
            (UNICODE_FEED, UNICODE_FEED),
            (OPML_FEED, OPML_FEED['xmlUrl']),
            (MONGO_FEED, MONGO_FEED.link),
        )

        for feed, url in cases:
            fsync = FeedSync(feed)
            self.assertEqual(fsync.url, url)

    @mock.patch('baleen.feed.feedparser.parse')
    def test_feedparser_wrapping(self, mock_feedparser):
        """
        Test the feedparser access by mocking feedparser calls
        """

        # Ensure that the mocking worked out for us
        assert mock_feedparser is feedparser.parse

        cases = (
            (STR_FEED, STR_FEED),
            (UNICODE_FEED, UNICODE_FEED),
            (OPML_FEED, OPML_FEED['xmlUrl']),
            (MONGO_FEED, MONGO_FEED.link),
        )

        for feed, url in cases:
            fsync  = FeedSync(feed)
            result = fsync.parse()
            mock_feedparser.assert_called_with(url)

    @mock.patch('baleen.feed.feedparser.parse')
    def test_feedparser_wrapping(self, mock_feedparser):
        """
        Test etag and modified blocking on feedparser for Feed objects
        """

        # Ensure that the mocking worked out for us
        assert mock_feedparser is feedparser.parse

        feed = Feed(link = u'https://mubi.com/notebook/posts.atom')
        feed.etag = 'abcdefg'

        # Test Case 1: etag but no modified
        result = FeedSync(feed).parse()
        mock_feedparser.assert_called_with(feed.link, etag=feed.etag)

        # Test Case 2: modified but no etag
        feed.etag = None
        feed.modified = "Fri, 11 Jun 2012 23:00:34 GMT"
        result = FeedSync(feed).parse()
        mock_feedparser.assert_called_with(feed.link, modified=feed.modified)

        # Test Case 3: modified and etag
        feed.etag = 'hijklmnop'
        result = FeedSync(feed).parse()
        mock_feedparser.assert_called_with(feed.link, etag=feed.etag)

    @mock.patch('baleen.feed.feedparser.parse')
    def test_feed_sync(self, mock_feedparser):
        """
        Test that sync updates the Feed object
        """
        # Ensure that the mocking worked out for us
        assert mock_feedparser is feedparser.parse

        # Give the mock feedparser a result!
        with open(RESULT, 'rb') as f:
            mock_feedparser.return_value = pickle.load(f)

        fsync  = FeedSync(MONGO_FEED)
        result = fsync.sync()

        # Fetch the feed from the database.
        self.assertEqual(Feed.objects.count(), 1)
        feed = Feed.objects.first()

        # Ensure that the various properties have been set.
        self.assertEqual(feed.etag, u'W/"29e84abdc28e3fa87709d1f309b7c214-gzip"')
        self.assertEqual(feed.modified, u'Wed, 02 Mar 2016 22:00:06 GMT')
        self.assertEqual(feed.version, u'rss20')
        self.assertEqual(feed.link, MONGO_FEED.link)
        self.assertIsNotNone(feed.fetched)

    @mock.patch('baleen.feed.feedparser.parse')
    def test_feed_sync_mongodb(self, mock_feedparser):
        """
        Test the sync MongoDB interaction
        """
        # Ensure that the mocking worked out for us
        assert mock_feedparser is feedparser.parse

        # Give the mock feedparser a result!
        with open(RESULT, 'rb') as f:
            mock_feedparser.return_value = pickle.load(f)

        fsync  = FeedSync(MONGO_FEED)

        # Test sync without save
        result = fsync.sync(save=False)
        self.assertEqual(Feed.objects.count(), 0)

        # Test sync with save
        result = fsync.sync()
        self.assertEqual(Feed.objects.count(), 1)

    @mock.patch('baleen.feed.feedparser.parse')
    def test_feed_sync_non_model(self, mock_feedparser):
        """
        Test the sync with a non-model feed.
        """
        # Ensure that the mocking worked out for us
        assert mock_feedparser is feedparser.parse

        # Give the mock feedparser a result!
        with open(RESULT, 'rb') as f:
            mock_feedparser.return_value = pickle.load(f)

        fsync  = FeedSync(OPML_FEED)

        # Test sync without save
        result = fsync.sync()
        self.assertEqual(Feed.objects.count(), 0)

    @mock.patch('baleen.feed.feedparser.parse')
    def test_feed_sync_not_changed_feed_raises_error(self, mock_feedparser):
        """
        Test the sync MongoDB interaction
        """
        # Ensure that the mocking worked out for us
        assert mock_feedparser is feedparser.parse

        # Give the mock feedparser a result!
        with open(RESULT, 'rb') as f:
            mock_feedparser.return_value = pickle.load(f)

        fsync  = FeedSync(MONGO_FEED)

        # First call to entries should not raise UnchangedFeedSyncError
        result = fsync.entries()
        self.assertEqual(Feed.objects.count(), 1)

        # TODO: feed.save() doesn't save some of fields including signature
        # So, we need to fix mongomock/mongoengine interaction, or just get rid of mongomock
        self.conn.baleen.feeds.find()[0]['signature'] = MONGO_FEED.signature
        self.conn.baleen.feeds.update_one({'_id': self.conn.baleen.feeds.find()[0]['_id']},
                                  {'$set': {'signature': MONGO_FEED.signature}},
                                  upsert=False)
        # Second should fail
        with self.assertRaises(UnchangedFeedSyncError):
            result = fsync.entries()

    @mock.patch('baleen.feed.feedparser.parse')
    def test_feed_sync_changed_feed(self, mock_feedparser):
        """
        Test the sync MongoDB interaction
        """
        # Ensure that the mocking worked out for us
        assert mock_feedparser is feedparser.parse

        # Give the mock feedparser a result!
        with open(RESULT, 'rb') as f:
            mock_feedparser.return_value = pickle.load(f)

        fsync  = FeedSync(MONGO_FEED)

        # First call to entries should not raise UnchangedFeedSyncError
        result = fsync.entries()
        self.assertEqual(Feed.objects.count(), 1)
        # changing list of entries should be enough to make feed ingested again
        mock_feedparser.return_value.entries.remove(mock_feedparser.return_value.entries[0])
        result = fsync.entries()
