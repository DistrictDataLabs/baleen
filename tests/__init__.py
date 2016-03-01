# tests
# Testing for the baleen module
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Sep 19 10:58:15 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
Testing for the baleen module
"""

##########################################################################
## Imports
##########################################################################

import unittest

##########################################################################
## Module Constants
##########################################################################

TEST_VERSION = "0.2" ## Also the expected version onf the package

##########################################################################
## Test Cases
##########################################################################

class InitializationTest(unittest.TestCase):

    def test_initialization(self):
        """
        Tests a simple world fact by asserting that 10*10 is 100
        """
        self.assertEqual(10*10, 100)

    def test_import(self):
        """
        Can import baleen
        """
        try:
            import baleen
        except ImportError:
            self.fail("Unable to import the baleen module!")

    def test_version(self):
        """
        Assert that the version is sane
        """
        import baleen
        self.assertEqual(TEST_VERSION, baleen.__version__)
