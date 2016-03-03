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
from baleen.exceptions import *

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

    def test_reraise(self):
        """
        Test the reraise decorator
        """

        # Test 1: Regular old reraise

        @reraise()
        def alpha():
            raise Exception("Should be a BaleenError")

        with self.assertRaises(BaleenError) as cm:
            alpha()

        e = cm.exception
        self.assertEqual(str(e), "Should be a BaleenError")
        self.assertTrue(hasattr(e, "original"))
        self.assertIsInstance(e.original, Exception)
        self.assertEqual(str(e.original), "Should be a BaleenError")

    def test_reraise_message(self):
        """
        Test the reraise decorator with a message
        """

        # Test 2: Reraise with a new message

        @reraise(message="I'm handling it!")
        def bravo():
            raise NotImplementedError("I'm not handling it!")

        with self.assertRaises(BaleenError) as cm:
            bravo()

        e = cm.exception
        self.assertEqual(str(e), "I'm handling it!")
        self.assertTrue(hasattr(e, "original"))
        self.assertIsInstance(e.original, NotImplementedError)
        self.assertEqual(str(e.original), "I'm not handling it!")

    def test_reraise_arguments(self):
        """
        Test the reraise decorator with all possible arguments
        """

        # Test 3: All possible arguments to reraise

        @reraise(klass=FeedTypeError, message="bad feed type", trap=TypeError)
        def charlie():
            raise TypeError("requires an integer")

        with self.assertRaises(FeedTypeError) as cm:
            charlie()

        e = cm.exception
        self.assertEqual(str(e), "bad feed type")
        self.assertTrue(hasattr(e, "original"))
        self.assertIsInstance(e.original, TypeError)
        self.assertEqual(str(e.original), "requires an integer")

    def test_reraise_trap(self):
        """
        Test the reraise decorator by missing the trap
        """

        # Test 4: Missing the trap

        @reraise(klass=FeedTypeError, message="bad feed type", trap=TypeError)
        def delta():
            raise ValueError("this should be the exception raised")

        with self.assertRaises(ValueError) as cm:
            delta()

        e = cm.exception
        self.assertEqual(str(e), "this should be the exception raised")
        self.assertFalse(hasattr(e, "original"))
