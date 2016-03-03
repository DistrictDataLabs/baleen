# test.utils_tests.test_timez
# Testing for the timez time helpers library.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Feb 21 15:33:18 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_timez.py [] benjamin@bengfort.com $

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

    def test_strptimez(self):
        """
        Test the parsing of timezone aware date strings
        """
        dtfmt = "%Y-%m-%dT%H:%M:%S%z"

        cases = (
            ('2012-12-27T12:53:12-0500', datetime(2012, 12, 27, 17, 53, 12, tzinfo=tzutc())),
            ('2012-12-27T12:53:12+0800', datetime(2012, 12, 27, 4, 53, 12, tzinfo=tzutc())),
        )

        for dtstr, dt in cases:
            self.assertEqual(dt, strptimez(dtstr, dtfmt))

        # Non-timezone case
        self.assertEqual(
            strptimez('2012-12-27T12:53:12', "%Y-%m-%dT%H:%M:%S"),
            datetime(2012, 12, 27, 12, 53, 12)
        )

    def test_strptimez_no_z(self):
        """
        Assert that strptimez works with no '%z'
        This should return a timezone naive datetime
        """
        dtfmt = "%a %b %d %H:%M:%S %Y"
        dtstr = self.localnow.strftime(dtfmt)
        self.assertEqual(strptimez(dtstr, dtfmt), self.localnow.replace(tzinfo=None))


    def test_strptimez_no_space(self):
        """
        Non-space delimited '%z' works
        """
        dtfmt = "%Y-%m-%dT%H:%M:%S%z"
        dtstr = self.localnow.strftime(dtfmt)
        self.assertEqual(strptimez(dtstr, dtfmt), self.utcnow)

    def test_begin_z(self):
        """
        Test fmt that begins with '%z'
        """
        dtfmt = "%z %H:%M:%S for %Y-%m-%d"
        dtstr = self.localnow.strftime(dtfmt)
        self.assertEqual(strptimez(dtstr, dtfmt), self.utcnow)

    def test_middle_z(self):
        """
        Test fmt that contains '%z'
        """
        dtfmt = "time is: %H:%M:%S %z on %Y-%m-%d "
        dtstr = self.localnow.strftime(dtfmt)
        self.assertEqual(strptimez(dtstr, dtfmt), self.utcnow)

    def test_timer(self):
        """
        Test the Timer context manager
        """
        with Timer() as t:
            time.sleep(1)

        self.assertGreater(t.finished, t.started)
        self.assertEqual(t.elapsed, t.finished-t.started)
        self.assertEqual(str(t), '1 seconds')
