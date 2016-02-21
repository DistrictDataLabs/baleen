# test.utils_tests.timez_tests
# Testing for the timez time helpers library.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Feb 21 15:33:18 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: timez_tests.py [] benjamin@bengfort.com $

"""
Testing for the timez time helpers library.
"""

##########################################################################
## Imports
##########################################################################

import unittest

from datetime import datetime
from dateutil.tz import tzutc
from baleen.utils.timez import *

##########################################################################
## Time Helper Functions Tests
##########################################################################

class TimezTests(unittest.TestCase):

    def test_non_naive_datetimes(self):
        """
        Assert that localnow and utcnow return non-naive datetimes
        """
        self.assertIsNotNone(localnow().tzinfo)
        self.assertIsNotNone(utcnow().tzinfo)

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
