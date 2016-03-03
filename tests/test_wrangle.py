# tests.test_wrangle
# Test the post wrangling module and functionality.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 22:38:08 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: .test_wrangle.py [] benjamin@bengfort.com $

"""
Test the post wrangling module and functionality.
"""

##########################################################################
## Imports
##########################################################################

import os
import pickle
import unittest

from .test_models import MongoTestMixin

try:
    from unittest import mock
except ImportError:
    import mock

from baleen.wrangle import *
from baleen.exceptions import *
from baleen.models import Feed, Post

##########################################################################
## Fixtures
##########################################################################

FIXTURES  = os.path.join(os.path.dirname(__file__), "fixtures")
RESULT    = os.path.join(FIXTURES, "feedparser_result.pickle")
FEED      = Feed(
    title = u'The Rumpus.net',
    link  = u'http://therumpus.net/feed/',
    urls  = {u'htmlurl': u'http://therumpus.net'}, category = u'books',
)


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code

        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception("HTTP {}".format(self.status_code))

    text = "Luke, I am your father!"

    if args[0] == 'http://example.com/vader/':
        return MockResponse(text, 200)

    return MockResponse("??", 404)

##########################################################################
## Test Wrangling Posts
##########################################################################

class PostWranglerTests(MongoTestMixin, unittest.TestCase):

    def setUp(self):
        super(PostWranglerTests, self).setUp()
        self.feed = FEED
        self.feed.save()

        with open(RESULT, 'rb') as f:
            self.entries = pickle.load(f).entries

    def test_wrangle_factory(self):
        """
        Test multiple types in the feed sync factory
        """

        for wrangle in PostWrangler.factory(self.entries, feed=self.feed):
            self.assertIsInstance(wrangle, PostWrangler)

    def test_wrangle_integration(self):
        """
        Test wrangling of all entries in the result.
        """
        self.assertEqual(Post.objects.count(), 0)
        for wrangle in PostWrangler.factory(self.entries, feed=self.feed):
            wrangle.wrangle()
            wrangle.wrangle() # Make sure that double wrangle does nothing.

        self.assertEqual(Post.objects.count(), 10)

        # Ensure there are no duplicates
        for wrangle in PostWrangler.factory(self.entries, feed=self.feed):
            with self.assertRaises(WranglingError) as cm:
                wrangle.wrangle()
            self.assertEqual(Post.objects.count(), 10)

    def test_is_wrangled(self):
        """
        Test the wrangling detection
        """
        wrangle = PostWrangler(self.entries[0])
        self.assertFalse(wrangle.is_wrangled())
        wrangle.wrangle()
        self.assertTrue(wrangle.is_wrangled())

    def test_save_not_save(self):
        """
        Test the wrangle interaction with the database
        """
        self.assertEqual(Post.objects.count(), 0)
        wrangle = PostWrangler(self.entries[0])

        # Don't save the wrangle
        wrangle.wrangle(False)
        self.assertEqual(Post.objects.count(), 0)

        # We've already wrangled so nothing should happen!
        wrangle.wrangle()
        self.assertEqual(Post.objects.count(), 0)

        # Try making something happen directly
        wrangle.wrangle().save()
        self.assertEqual(Post.objects.count(), 1)

        # Toss in something else entirely
        wrangle = PostWrangler(self.entries[1])
        wrangle.wrangle()
        self.assertEqual(Post.objects.count(), 2)

    def test_feed_or_not(self):
        """
        Test can be saved with or without a feed
        """
        withfeed = PostWrangler(self.entries[0], feed=self.feed)
        nofeed   = PostWrangler(self.entries[1])

        post = withfeed.wrangle()
        self.assertEqual(post.feed, self.feed)

        post = nofeed.wrangle()
        self.assertIsNone(post.feed)

    @mock.patch('baleen.wrangle.requests.get', side_effect=mocked_requests_get)
    def test_fetch_not_wrangled(self, mock_requests):
        """
        Assert that fetch requires wrangling
        """
        assert mock_requests is requests.get

        wrangle = PostWrangler(self.entries[0], feed=self.feed)
        with self.assertRaises(FetchError):
            wrangle.fetch()

    @mock.patch('baleen.wrangle.requests.get', side_effect=mocked_requests_get)
    def test_fetch_overwrites_content(self, mock_requests):
        """
        Test that the fetch overwrites content.
        """
        assert mock_requests is requests.get

        wrangle = PostWrangler(self.entries[0], feed=self.feed)
        wrangle.wrangle()
        self.assertEqual(Post.objects.count(), 1)

        wrangle.post.url = 'http://example.com/vader/'
        post = wrangle.fetch()
        self.assertEqual(Post.objects.count(), 1)
        self.assertNotEqual(post.created, post.updated)

        self.assertEqual(post.content, "Luke, I am your father!")

    @mock.patch('baleen.wrangle.requests.get', side_effect=mocked_requests_get)
    def test_fetch_no_save(self, mock_requests):
        """
        Test that the fetch does not save on demand.
        """
        assert mock_requests is requests.get

        wrangle = PostWrangler(self.entries[0], feed=self.feed)
        wrangle.wrangle()
        self.assertEqual(Post.objects.count(), 1)

        wrangle.post.url = 'http://example.com/vader/'
        wrangle.fetch(save=False)
        self.assertEqual(Post.objects.count(), 1)

        post = Post.objects.first()
        self.assertDateTimeEqual(post.created, post.updated)
        self.assertNotEqual(post.content, "Luke, I am your father!")

    @mock.patch('baleen.wrangle.requests.get', side_effect=mocked_requests_get)
    def test_fetch_raises_404(self, mock_requests):
        """
        Test that fetch raises exception on HTTP error
        """
        assert mock_requests is requests.get

        wrangle = PostWrangler(self.entries[0], feed=self.feed)
        wrangle.wrangle()
        self.assertEqual(Post.objects.count(), 1)

        with self.assertRaises(FetchError):
            wrangle.post.url = 'http://example.com/obiwan/'
            wrangle.fetch()
        
