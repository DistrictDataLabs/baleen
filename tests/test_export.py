# tests.test_export
# Test the export module - to generate a corpus for machine learning.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Feb 21 15:49:18 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_export.py [2988c53] benjamin@bengfort.com $

"""
Test the export module - to generate a corpus for machine learning.
"""

##########################################################################
## Imports
##########################################################################

import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from baleen.export import *
from baleen.exceptions import ExportError


##########################################################################
## Export Tests
##########################################################################

class ExportTests(unittest.TestCase):

    def test_scheme_specification(self):
        """
        Assert that only known schemes are allowed.
        """

        # Make sure good schemes don't error
        for scheme in SCHEMES:
            try:
                exporter = MongoExporter("/tmp/corpus", scheme=scheme)
            except ExportError:
                self.fail("Could not use expected scheme, {}".format(scheme))

        # Make sure bad schemes do error
        for scheme in ('bson', 'xml', 'yaml', 'foo', 'bar'):
            with self.assertRaises(ExportError):
                exporter = MongoExporter("/tmp/corpus", scheme=scheme)
