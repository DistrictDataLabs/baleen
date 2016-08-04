# tests
# Testing for the baleen version module
#
# Author:   Will Voorhees <developer@willz.org>
# Created:  Thu Jun 02 17:06:15 2016 -0700
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#

"""
Testing for the baleen module
"""

##########################################################################
## Imports
##########################################################################

import unittest
import baleen

##########################################################################
## Test Cases
##########################################################################

class GetVersionTest(unittest.TestCase):

    def test_final_version(self):
        """
        Assert that the final version is correct
        """
        test_version_info = {
            'major': 0,
            'minor': 3,
            'micro': 3,
            'releaselevel': 'final',
            'serial': 0,
        }
        
        self.assertEqual("0.3.3", baleen.get_version(short=True,version_info=test_version_info))
        self.assertEqual("0.3.3", baleen.get_version(short=False,version_info=test_version_info))

    def test_non_final_version(self):
        """
        Assert that the non-final version is correct
        """
        test_version_info = {
            'major': 0,
            'minor': 3,
            'micro': 3,
            'releaselevel': 'alpha',
            'serial': 0,
        }

        self.assertEqual("0.3.3", baleen.get_version(short=True,version_info=test_version_info))
        self.assertEqual("0.3.3a0", baleen.get_version(short=False, version_info=test_version_info))
