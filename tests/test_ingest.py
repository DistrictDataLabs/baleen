# tests.test_ingest
# Test the ingestor mechanism in an integration fashion.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Mar 03 13:01:12 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_ingest.py [df0c71b] benjamin@bengfort.com $

"""
Test the ingestor mechanism in an integration fashion.
"""

##########################################################################
## Imports
##########################################################################

import unittest

from .test_models import MongoTestMixin
from unittest import mock
from unittest.mock import call
from collections import Counter

import baleen.models as db
from baleen.exceptions import *
from baleen.feed import FeedSync
from baleen.ingest import stype, Ingestor, MongoIngestor, OPMLIngestor
from baleen.models import Feed, Post
from baleen.utils.decorators import reraise
from baleen.utils.logger import IngestLogger

from mongoengine.errors import NotUniqueError

##########################################################################
## Helper Functions
##########################################################################

ACTION_METHODS = ('started', 'finished', 'failed', 'process')

def get_ingest_mock(klass=Ingestor):
    """
    Mocks all functions of the ingestor that are called in ingest.
    This means there should be NO side effects when ingest is called.
    """
    # Verify and create ingestor class
    ingestor = klass()
    verify_ingest_mock(ingestor)

    # Remove action methods
    for method in ACTION_METHODS:
        setattr(ingestor, method, mock.MagicMock())

    return ingestor


def verify_ingest_mock(ingestor):
    """
    Ensures that no methods other than action methods are called
    """
    ingestor = mock.create_autospec(ingestor, instance=True)
    reset_mock_method(ingestor, 'ingest')
    ingestor.ingest()

    for method in ingestor._mock_methods:
        action = getattr(ingestor, method)
        if method not in ACTION_METHODS:
            if hasattr(action, 'assert_not_called'):
                action.assert_not_called()


def reset_mock_method(obj, method):
    """
    Resets a mock object's method to the orignal
    """
    klass  = obj.__class__
    action = getattr(klass, method)

    setattr(obj, method, action.__get__(obj, klass))
    return obj

def change_class_logger(mock_logger, klass):
    setattr(klass, 'logger', mock_logger)

##########################################################################
## Test Ingestor
##########################################################################

class IngestorTests(MongoTestMixin, unittest.TestCase):

    def test_stype_helper(self):
        """
        Test the stype helper function
        """
        self.assertEqual(stype(BaleenError("Bad things!")), BaleenError.__name__)

    def test_stype_embed_helper(self):
        """
        Test stype on reraises decorators.
        """

        @reraise(BaleenError)
        def badfunc():
            raise TypeError("This is clearly the wrong type!")

        try:
            badfunc()
        except BaleenError as e:
            self.assertEqual(stype(e), "BaleenError (TypeError)")

    def test_ingestor_hooks(self):
        """
        Test the started and finished ingestor hooks
        """

        # Create Ingestor and call the entry point method
        ingestor = get_ingest_mock()
        ingestor.ingest()

        # Assert that started and finished were called, and failed wasn't.
        ingestor.started.assert_called_once_with()
        ingestor.finished.assert_called_once_with()
        ingestor.failed.assert_not_called()

    def test_ingestor_failed_hook(self):
        """
        Test the started and failed ingestor hooks
        """

        ingestor = get_ingest_mock()
        ingestor.process.side_effect = Exception("Things went wrong!")

        # Call the entry point method
        with self.assertRaises(Exception) as cm:
            ingestor.ingest()

        # Assert that started and finished were called, and failed wasn't.
        ingestor.started.assert_called_once_with()
        ingestor.finished.assert_not_called()
        ingestor.failed.assert_called_once_with(cm.exception)

    def test_ingestor_state(self):
        """
        Ensure that the ingestor state is correctly modified
        """
        ingestor = get_ingest_mock()

        self.assertIsNone(ingestor.jobid)
        self.assertIsNone(ingestor.timer)

        ingestor.ingest()

        self.assertIsNotNone(ingestor.jobid)
        self.assertIsNotNone(ingestor.timer)

    def test_ingestor_finished(self):
        """
        Ensure that the Ingestor finished method has no errors
        """
        ingestor = Ingestor()
        mock_logger = mock.MagicMock()
        change_class_logger(mock_logger, ingestor.__class__)

        ingestor.finished()

        logger_calls = [
            call("Processed 0 (0 unchanged) feeds (None) 0 posts with 0 errors and 0 duplicate posts"),
            call("Ingestor job None finished"),
        ]
        mock_logger.info.assert_has_calls(logger_calls, any_order=True)

    def test_process_feed(self):
        """
        Ensure process_feed can be called successfully
        """
        ingestor = get_ingest_mock()
        test_post = Post(title="My Awesome Post", content="socks")
        ingestor.process_post = mock.MagicMock(return_value=test_post)

        fsync = FeedSync("http://somesite.net/feeds")
        fsync.entries = mock.MagicMock(return_value=["stuff"])
        ingestor.process_feed(fsync)

        self.assertEqual(ingestor.counts["posts"], 1)
        self.assertEqual(ingestor.counts["errors"], 0)

    def test_process_feed_with_error(self):
        """
        Ensure process_feed behaves correctly on error
        """
        ingestor = get_ingest_mock()
        ingestor.process_post = mock.MagicMock()
        ingestor.process_post.side_effect = WranglingError("Things went wrong!")

        fsync = FeedSync("http://somesite.net/feeds")
        fsync.entries = mock.MagicMock(return_value=["stuff"])
        ingestor.process_feed(fsync)

        self.assertEqual(ingestor.counts["posts"], 0)
        self.assertEqual(ingestor.counts["errors"], 1)
        self.assertEqual(ingestor.errors["WranglingError"], 1)

    def test_process(self):
        """
        Ensure process can be called successfully
        """
        feed = Feed(title="A News Feed", category="news", link="https://example.com/feed.atom")
        ingestor = Ingestor(feeds=[feed])
        ingestor.process_feed = mock.MagicMock()

        ingestor.process()

        self.assertEqual(ingestor.counts["feeds"], 1)
        self.assertEqual(ingestor.counts["feed_error"], 0)
        self.assertFalse(ingestor.errors) # Empty is considered 'False'

    def test_process_with_error(self):
        """
        Ensure process behaves correctly on error
        """
        feed = Feed(title="A News Feed", category="news", link="https://example.com/feed.atom")
        ingestor = Ingestor(feeds=[feed])
        ingestor.process_feed = mock.MagicMock()
        ingestor.process_feed.side_effect = SynchronizationError("Things went wrong!")

        ingestor.process()

        self.assertEqual(ingestor.counts["feeds"], 0)
        self.assertEqual(ingestor.counts["feed_error"], 1)
        self.assertEqual(ingestor.errors["SynchronizationError"], 1)

    def test_process_post(self):
        """
        Ensure process_post can be called successfully
        """
        post = Post(title="My Awesome Post", content="socks", url="http://example.com/socks.html")
        post.wrangle = mock.MagicMock()
        post.fetch = mock.MagicMock()

        ingestor = get_ingest_mock()
        ingestor.process_post(post)

        self.assertEqual(ingestor.counts["fetch_error"], 0)
        self.assertFalse(ingestor.errors) # Empty is considered 'False'

    def test_process_post_with_error(self):
        """
        Ensure process_post behaves correctly on error
        """
        post = Post(title="My Awesome Post", content="socks", url="http://example.com/socks.html")
        post.wrangle = mock.MagicMock()
        post.fetch = mock.MagicMock()
        post.fetch.side_effect = FetchError("Things went wrong!")

        ingestor = get_ingest_mock()
        ingestor.process_post(post)

        self.assertEqual(ingestor.counts["fetch_error"], 1)
        self.assertEqual(ingestor.errors["FetchError"], 1)

    def test_process_post_with_duplicate_post_error(self):
        """
        Ensure process_post behaves correctly on duplicate post
        """
        post = Post(title="Some Duplicate Post", content="socks", url="http://example.com/socks.html")
        post.wrangle = mock.MagicMock()
        duplicate_post_error = WranglingError("This is a duplicate")
        duplicate_post_error.original = NotUniqueError("Document already exists")
        post.wrangle.side_effect = duplicate_post_error
        post.fetch = mock.MagicMock()

        ingestor = get_ingest_mock()
        ingestor.process_post(post)

        self.assertEqual(ingestor.counts["duplicate_posts"], 1)

    def test_process_post_with_wrangle_error_on_non_duplicate(self):
        """
        Ensure process_post behaves correctly without a duplicate post
        """
        post = Post(title="Some Duplicate Post", content="socks", url="http://example.com/socks.html")
        post.wrangle = mock.MagicMock()
        wrangle_error = WranglingError("There was a wrangle error")
        wrangle_error.original = Exception("Some non-duplicate related error")
        post.wrangle.side_effect = wrangle_error
        post.fetch = mock.MagicMock()

        ingestor = get_ingest_mock()
        with self.assertRaises(WranglingError):
            ingestor.process_post(post)

        self.assertEqual(ingestor.counts["duplicate_posts"], 0)

class MongoIngestorTests(MongoTestMixin, unittest.TestCase):

    def test_mongo_ingestor_finished(self):
        """
        Ensure that the MongoIngestor finished method has no errors
        """
        ingestor = MongoIngestor()
        mock_logger = mock.MagicMock()
        change_class_logger(mock_logger, ingestor.__class__)

        # Instance mocked actions
        mock_job = mock.MagicMock()
        ingestor.job = mock_job

        # Call
        ingestor.finished()

        # Assert expected behavior
        logger_calls = [
            call("Processed 0 (0 unchanged) feeds (None) 0 posts with 0 errors and 0 duplicate posts"),
            call("MongoIngestor job None finished"),
        ]
        mock_logger.info.assert_has_calls(logger_calls, any_order=True)

        mock_job.save.assert_called_once_with()
        self.assertEqual(mock_job.reason, "OK")

    def test_mongo_ingestor_failed(self):
        """
        Ensure that the MongoIngestor failed method has no errors
        """
        ingestor = MongoIngestor()
        mock_logger = mock.MagicMock()
        change_class_logger(mock_logger, ingestor.__class__)

        # Instance mocked actions
        mock_job = mock.MagicMock()
        ingestor.job = mock_job

        # Call
        ingestor.failed(FetchError("Something went wrong!"))

        # Assert expected behavior
        logger_calls = [
            call.error("Ingestion Error: Something went wrong!"),
            call.critical("MongoIngestor job None failed!"),
        ]
        mock_logger.assert_has_calls(logger_calls, any_order=True)

        self.assertTrue(mock_job.failed)
        mock_job.save.assert_called_once_with()
