# test.test_utils.test_decorators
# Testing the decorators utility package.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 19:06:34 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_decorators.py [] benjamin@bengfort.com $

"""
Testing the decorators utility package.
"""

##########################################################################
## Imports
##########################################################################

import time
import unittest

from baleen.utils.decorators import *
from baleen.utils.timez import Timer

try:
    from unittest import mock
except ImportError:
    import mock


##########################################################################
## Decorators Tests
##########################################################################

class DecoratorsTests(unittest.TestCase):
    """
    Basic decorators utility tests.
    """

    def test_memoized(self):
        """
        Test the memoized property
        """

        class Thing(object):

            @memoized
            def attr(self):
                return 42

        thing = Thing()
        self.assertFalse(hasattr(thing, '_attr'))
        self.assertEqual(thing.attr, 42)
        self.assertTrue(hasattr(thing, '_attr'))

    def test_timeit(self):
        """
        Test the timeit decorator
        """

        @timeit
        def myfunc():
            return 42

        output = myfunc()
        self.assertEqual(len(output), 2)
        result, timer = output
        self.assertEqual(result, 42)
        self.assertTrue(isinstance(timer, Timer))
