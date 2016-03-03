# tests.test_ingest
# Test the ingestor mechanism in an integration fashion.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Mar 03 13:01:12 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_ingest.py [] benjamin@bengfort.com $

"""
Test the ingestor mechanism in an integration fashion.
"""

##########################################################################
## Imports
##########################################################################

import unittest

from .test_models import MongoTestMixin

try:
    from unittest import mock
except ImportError:
    import mock

import baleen.models as db

from baleen.ingest import stype
from baleen.ingest import Ingestor
from baleen.ingest import MongoIngestor
from baleen.ingest import OPMLIngestor
from baleen.utils.decorators import reraise
from baleen.exceptions import *
from baleen.utils.logger import IngestLogger


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
