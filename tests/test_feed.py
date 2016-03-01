# tests.test_feed
# Test the feed module - the main entry point to Baleen
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Feb 21 15:49:18 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_feed.py [] benjamin@bengfort.com $

"""
Test the feed module - the main entry point to Baleen
"""

##########################################################################
## Imports
##########################################################################

import os
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from baleen.feed import *
from urlparse import urlparse

##########################################################################
## Feed Ingestor Tests
##########################################################################

class FeedIngestorTests(unittest.TestCase):
    """
    Test the feed ingestor base class.
    """

    def test_interface(self):
        """
        Assert that the feed ingestor is an interface.
        """
        ingestor = FeedIngestor()
        with self.assertRaises(NotImplementedError):
            feeds = list(ingestor.get_feed_urls())

        with self.assertRaises(NotImplementedError):
            feeds = ingestor.ingest()

        ingestor.feed_urls = ['a', 'b', 'c']
        self.assertEqual(list(ingestor.get_feed_urls()), ingestor.feed_urls)


##########################################################################
## Fixtures
##########################################################################

FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")
FEEDLY   = os.path.join(FIXTURES, "feedly.opml")

##########################################################################
## OPML Feed Ingestor Tests
##########################################################################

class OPMLFeedIngestorTests(unittest.TestCase):
    """
    Test the OPML feed ingestor.
    """

    def test_get_feed_urls(self):
        """
        Test the feed url generator on an OPML feed ingestor.
        """

        ingestor = OPMLFeedIngestor(FEEDLY)
        feeds = 0

        for feed in ingestor.get_feed_urls():
            feeds += 1
            url = urlparse(feed)
            self.assertNotEqual(url.scheme, '')
            self.assertNotEqual(url.netloc, '')
            self.assertNotEqual(url.path, '')

        self.assertEqual(feeds, 102)

    def test_len(self):
        """
        Test the length method on the OPML feed ingestor.
        """

        ingestor = OPMLFeedIngestor(FEEDLY)
        self.assertEqual(len(ingestor), 102)
