# tests.utils_tests.test_logger
# Simple tests for the logger module.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Mar 03 11:52:06 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_logger.py [] benjamin@bengfort.com $

"""
Simple tests for the logger module.
"""

##########################################################################
## Imports
##########################################################################

import getpass
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from baleen.utils.logger import *


##########################################################################
## Module Helpers
##########################################################################

PREFIX = "TEST LOG"
IGNORE = "IGNORE: This should not be in a log file or database!"

def tmsgf(message, prefix=PREFIX, ignore=IGNORE):
    return "{}: {} ({})".format(prefix, message, ignore)

##########################################################################
## Logger Test
##########################################################################

class IngestLoggerTests(unittest.TestCase):
    """
    Simply exercises the methods of the logger.
    """

    @mock.patch('baleen.utils.logger.IngestLogger.logger')
    def test_log_extra(self, mock_logger):
        """
        Assert that extra (user) is passed to logger
        """

        logger  = IngestLogger()

        assert logger.logger is mock_logger

        message = tmsgf("Do not double space after a period!")
        logger.log(logging.DEBUG, message)

        mock_logger.log.assert_called_with(logging.DEBUG, message, extra={'user': getpass.getuser()})

    @mock.patch('baleen.utils.logger.IngestLogger.logger')
    def test_log_debug(self, mock_logger):
        """
        Test the debug logger
        """

        logger  = IngestLogger()

        assert logger.logger is mock_logger

        message = tmsgf("All CAPS is not shouting!")
        logger.debug(message)

        mock_logger.log.assert_called_with(logging.DEBUG, message, extra=mock.ANY)

    @mock.patch('baleen.utils.logger.IngestLogger.logger')
    def test_log_info(self, mock_logger):
        """
        Test the info logger
        """

        logger  = IngestLogger()

        assert logger.logger is mock_logger

        message = tmsgf("Birds and Bees Flock with Seas!")
        logger.info(message)

        mock_logger.log.assert_called_with(logging.INFO, message, extra=mock.ANY)

    @mock.patch('baleen.utils.logger.IngestLogger.logger')
    def test_log_warn(self, mock_logger):
        """
        Test the warn logger
        """

        logger  = IngestLogger()

        assert logger.logger is mock_logger

        message = tmsgf("You shouldn't touch that hot stove!")
        logger.warn(message)

        mock_logger.log.assert_called_with(logging.WARNING, message, extra=mock.ANY)

    @mock.patch('baleen.utils.logger.IngestLogger.logger')
    def test_log_error(self, mock_logger):
        """
        Test the error logger
        """

        logger  = IngestLogger()

        assert logger.logger is mock_logger

        message = tmsgf("Someone let the rooster into the hen house!")
        logger.error(message)

        mock_logger.log.assert_called_with(logging.ERROR, message, extra=mock.ANY)

    @mock.patch('baleen.utils.logger.IngestLogger.logger')
    def test_log_critical(self, mock_logger):
        """
        Test the critical logger
        """

        logger  = IngestLogger()

        assert logger.logger is mock_logger

        message = tmsgf("Someone let the fox into the hen house!")
        logger.critical(message)

        mock_logger.log.assert_called_with(logging.CRITICAL, message, extra=mock.ANY)
