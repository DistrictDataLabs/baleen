# test.utils_tests.test_timez
# Testing for the timez time helpers library.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Feb 21 15:33:18 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_timez.py [df0c71b] benjamin@bengfort.com $

"""
Testing for the timez time helpers library.
"""

##########################################################################
## Imports
##########################################################################

import time
import unittest

from datetime import datetime
from dateutil.tz import tzutc
from baleen.utils.timez import *

##########################################################################
## Helper Functions Test Cases
##########################################################################

class TimezHelpersTests(unittest.TestCase):

    def setUp(self):
        self.localnow = datetime.now(tzlocal()).replace(microsecond=0)
        self.utcnow   = self.localnow.astimezone(tzutc())

    def tearDown(self):
        self.localnow = self.utcnow = None

    def test_non_naive_datetimes(self):
        """
        Assert that localnow and utcnow return non-naive datetimes
        """
        self.assertIsNotNone(localnow().tzinfo)
        self.assertIsNotNone(utcnow().tzinfo)

    def test_humanizedelta(self):
        """
        Test the humanize delta function to convert seconds
        """
        cases = (
            (12512334, "144 days 19 hours 38 minutes 54 seconds"),
            (34321, "9 hours 32 minutes 1 second"),
            (3428, "57 minutes 8 seconds"),
            (1, "1 second"),
            (0.21, "0 second"),
        )

        for seconds, expected in cases:
            self.assertEqual(humanizedelta(seconds=seconds), expected)

    def test_humanizedelta_milliseconds(self):
        """
        Test the humanize delta function to conver milliseconds
        """

        # Case with seconds already there
        self.assertEqual(humanizedelta(seconds=10, milliseconds=2000), '12 seconds')

        # Case without seconds present
        self.assertEqual(humanizedelta(milliseconds=456875), '7 minutes 36 seconds')

    def test_timer(self):
        """
        Test the Timer context manager
        """
        with Timer() as t:
            time.sleep(1)

        self.assertGreater(t.finished, t.started)
        self.assertEqual(t.elapsed, t.finished-t.started)
        self.assertEqual(str(t), '1 seconds')
