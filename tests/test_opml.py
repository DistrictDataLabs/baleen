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

try:
    from unittest import mock
except ImportError:
    import mock

from baleen.opml import OPML

##########################################################################
## Fixtures
##########################################################################

FIXTURES = os.path.join(os.path.dirname(__file__), "..", "fixtures")
FEEDLY   = os.path.join(FIXTURES, "feedly.opml")

##########################################################################
## Test Ingestion
##########################################################################

class IngestionTests(unittest.TestCase):

    @unittest.skip("not implemented yet")
    def test_ingest_integrated(self):
        """
        Test the integration of the ingest helper function.
        """
        raise NotImplementedError("Not Implemented Yet")


##########################################################################
## OPML Reader Test
##########################################################################

class OPMLTests(unittest.TestCase):

    def test_fixture(self):
        """
        Assert the required opml fixture is available.
        """
        self.assertTrue(os.path.exists(FEEDLY))
        self.assertTrue(os.path.isfile(FEEDLY))

    def test_categories(self):
        """
        Test the OPML categories listing
        """
        opml = OPML(FEEDLY)
        expected = [
            u'cooking',
            u'cinema',
            u'gaming',
            u'tech',
            u'essays',
            u'business',
            u'design',
            u'sports',
            u'books',
            u'data science',
            u'do it yourself'
        ]

        self.assertEqual(list(opml.categories()), expected)

    def test_length(self):
        """
        Test the OPML len built in
        """
        opml = OPML(FEEDLY)
        self.assertEqual(len(opml), 102)

    def test_counts(self):
        """
        Test the OPML category counter and item iterator
        """
        opml = OPML(FEEDLY)
        expected = {
            'cooking': 9,
            'cinema': 10,
            'gaming': 8,
            'tech': 14,
            'essays': 2,
            'business': 8,
            'design': 15,
            'sports': 7,
            'books': 6,
            'data science': 15,
            'do it yourself': 8,
        }
        counts = opml.counts()

        for key, val in expected.items():
            self.assertIn(key, counts)
            self.assertEqual(counts[key], val)

    def test_item_iterator_detail(self):
        """
        Test the XML result returned from OPML iteration
        """

        opml  = OPML(FEEDLY)
        attrs = ['category', 'title', 'text', 'htmlUrl', 'xmlUrl', 'type']
        for item in opml:
            self.assertTrue(isinstance(item, dict))
            self.assertEqual(item.keys(), attrs)
