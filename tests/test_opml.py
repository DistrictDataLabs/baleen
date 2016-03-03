# tests.test_opml
# Testing for the OPML reader and ingestion function.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Feb 19 08:50:19 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_opml.py [] benjamin@bengfort.com $

"""
Testing for the OPML reader and ingestion function.
"""

##########################################################################
## Imports
##########################################################################

import os
import unittest

from .test_models import MongoTestMixin

try:
    from unittest import mock
except ImportError:
    import mock

from baleen.opml import OPML, load_opml
from baleen.models import Feed

##########################################################################
## Fixtures
##########################################################################

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
FEEDLY   = os.path.join(FIXTURES, "feedly.opml")

##########################################################################
## Test Load OPML command
##########################################################################

class LoadOPMLTests(MongoTestMixin, unittest.TestCase):

    def test_load_opml_integrated(self):
        """
        Test the integration of the ingest helper function
        """
        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(load_opml(FEEDLY), 36)
        self.assertEqual(Feed.objects.count(), 36)

        for feed in Feed.objects():
            self.assertIn('xmlUrl', feed.urls)
            self.assertIn('htmlUrl', feed.urls)

    def test_load_opml_no_duplicates(self):
        """
        Assert multiple calls to the load_opml creates no duplicates
        """
        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(load_opml(FEEDLY), 36)
        self.assertEqual(Feed.objects.count(), 36)

        for _ in xrange(10):
            self.assertEqual(load_opml(FEEDLY), 0)
            self.assertEqual(Feed.objects.count(), 36)

##########################################################################
## OPML Reader Test
##########################################################################

class OPMLTests(unittest.TestCase):

    def test_fixture(self):
        """
        Assert the required opml fixture is available
        """
        self.assertTrue(os.path.exists(FEEDLY))
        self.assertTrue(os.path.isfile(FEEDLY))

    def test_categories(self):
        """
        Test the OPML categories listing
        """
        opml = OPML(FEEDLY)
        expected = [
            u'news',
            u'do it yourself',
            u'business',
            u'gaming',
            u'data science',
            u'essays',
            u'politics',
            u'tech',
            u'cinema',
            u'books',
            u'sports',
            u'cooking',
            u'design'
        ]

        print list(opml.categories())

        self.assertEqual(list(opml.categories()), expected)

    def test_length(self):
        """
        Test the OPML len built in
        """
        opml = OPML(FEEDLY)
        self.assertEqual(len(opml), 36)

    def test_counts(self):
        """
        Test the OPML category counter and item iterator
        """
        opml = OPML(FEEDLY)
        expected = {
            'cooking': 4,
            'cinema': 3,
            'gaming': 3,
            'tech': 3,
            'essays': 2,
            'business': 3,
            'design': 2,
            'sports': 3,
            'books': 3,
            'data science': 4,
            'do it yourself': 2,
            'news': 2,
            'politics': 2,
        }
        counts = opml.counts()

        for key, val in expected.items():
            self.assertIn(key, counts)
            self.assertEqual(
                counts[key], val,
                "{} mismatch: {} vs {}".format(key, counts[key], val)
            )

    def test_item_iterator_detail(self):
        """
        Test the XML result returned from OPML iteration
        """

        opml  = OPML(FEEDLY)
        attrs = ['category', 'title', 'text', 'htmlUrl', 'xmlUrl', 'type']
        for item in opml:
            self.assertTrue(isinstance(item, dict))
            self.assertEqual(item.keys(), attrs)
