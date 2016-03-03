# tests.test_models
# Testing for the mongoengine models (basic stuff).
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 21:11:08 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_models.py [] benjamin@bengfort.com $

"""
Testing for the mongoengine models (basic stuff).
"""

##########################################################################
## Imports
##########################################################################

import unittest
import mongoengine as me

from mongomock import MongoClient as MockMongoClient

try:
    from unittest import mock
except ImportError:
    import mock

from baleen.models import *


##########################################################################
## Mongo Test Mixin
##########################################################################

class MongoTestMixin(object):

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

    def assertDateTimeEqual(self, dta, dtb):
        """
        Assert that two datetimes are within 1 second of each other
        """
        dta = dta.replace(microsecond=0)
        dtb = dta.replace(microsecond=0)

        if dta.second != dtb.second:
            self.assertLessThanEqual(
                abs(dta.second - dtb.second), 1, "datetimes are not one second apart!"
            )
            dta = dta.replace(second=0)
            dtb = dtb.replace(second=0)

        self.assertEqual(dta, dtb)

##########################################################################
## Feed Model Tests
##########################################################################

class FeedModelTests(MongoTestMixin, unittest.TestCase):

    def test_link_requred(self):
        """
        Assert that the feed link is required
        """
        feed = Feed(title="My Awesome Feed", category="socks")
        with self.assertRaises(me.ValidationError):
            feed.save()

    def test_created_updated(self):
        """
        Ensure the feed updated timestamp is tracked
        """
        feed = Feed(title="A News Feed", category="news", link="https://example.com/feed.atom")
        feed.save()

        self.assertIsNotNone(feed.created)
        self.assertIsNotNone(feed.updated)
        self.assertDateTimeEqual(feed.created, feed.updated)

        feed.title = "An Olds Feed"
        feed.save()
        self.assertNotEqual(feed.created, feed.updated)

    def test_properties(self):
        """
        Test the properties of the feed model
        """
        feed = Feed(title="A News Feed", category="news", link="https://example.com/feed.atom")
        feed.save()

        self.assertEqual(feed.xmlurl, feed.link)
        self.assertIsNone(feed.htmlurl)

        feed.urls = {'htmlUrl': 'https://example.com/'}
        feed.save()

        self.assertEqual(feed.htmlurl, 'https://example.com/')

    def test_stringify(self):
        """
        Test the stringification of a feed
        """
        feed = Feed(category="news", link="https://example.com/feed.atom")
        feed.save()

        self.assertEqual(str(feed), feed.link)

        feed.title = "A News Feed"
        feed.save()

        self.assertEqual(str(feed), feed.title)


##########################################################################
## Post Model Tests
##########################################################################

class PostModelTests(MongoTestMixin, unittest.TestCase):

    def test_url_requred(self):
        """
        Assert that the post url is required
        """
        post = Post(title="My Awesome Post", content="socks")
        with self.assertRaises(me.ValidationError):
            post.save()

    def test_created_updated(self):
        """
        Ensure the post updated timestamp is tracked
        """
        post = Post(title="My Awesome Post", content="socks", url="http://example.com/socks.html")
        post.save()

        self.assertIsNotNone(post.created)
        self.assertIsNotNone(post.updated)
        self.assertDateTimeEqual(post.created, post.updated)

        post.title = "My even more awesome Post!"
        post.save()
        self.assertNotEqual(post.created, post.updated)

    def test_content_hashing(self):
        """
        Test the automatic hashing of content
        """
        post = Post(content="socks", url="http://example.com/socks.html")
        self.assertIsNone(post.signature)
        post.save()

        self.assertIsNotNone(post.signature)
        self.assertEqual(post.signature, '54f6d9fbe8ee576f82d6eb7e4d1d55691a1f0b7bd956246d3de56ee84bd1d333')

    def test_stringify(self):
        """
        Test the stringification of a post
        """
        post = Post(content="socks", signature="abc", url="http://example.com/socks.html")
        post.save()

        self.assertEqual(str(post), post.url)

        post.title = "My Awesome Post"
        post.save()

        self.assertEqual(str(post), post.title)
