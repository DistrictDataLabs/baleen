# tests.test_export
# Test the export module - to generate a corpus for machine learning.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Feb 21 15:49:18 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_export.py [] benjamin@bengfort.com $

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
