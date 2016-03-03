# tests.utils_tests.test_mongolog
# Simple tests for logging to MongoDB
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Mar 03 11:53:46 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_mongolog.py [] benjamin@bengfort.com $

"""
Simple tests for logging to MongoDB
"""

##########################################################################
## Imports
##########################################################################

import logging
import unittest

from mongomock import MongoClient as MockMongoClient

try:
    from unittest import mock
except ImportError:
    import mock

from baleen.utils import mongolog as ml
from .test_logger import tmsgf

##########################################################################
## Mongo Log Handler Tests
##########################################################################

class MongoLogHandlerTests(unittest.TestCase):
    """
    Simply exercises the methods of the logger.
    """

    @mock.patch('baleen.utils.mongolog.MongoClient', MockMongoClient)
    def test_logging_to_mongo(self):
        """
        Test the mongo log handler and logging to mongo
        """
        assert ml.MongoClient is MockMongoClient

        handler = ml.MongoHandler(level=logging.DEBUG)
        self.assertIsInstance(handler.connection, MockMongoClient)

        # Ensure there is nothing in the database.
        self.assertEqual(handler.collection.count(), 0)

        # Create the logging instance.
        logger = logging.getLogger('test.mongo.logger.demo')
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        # Log a message
        logger.info(tmsgf("This is a test of the mongo logger"))

        # Ensure there is now a log message
        self.assertEqual(handler.collection.count(), 1)
