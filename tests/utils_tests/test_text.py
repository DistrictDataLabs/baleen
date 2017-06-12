# test.utils_tests.test_text
# Testing for the text helpers library.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat Jun 03 18:48:00 2017 -0400
#
# Copyright (C) 2017 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_text.py [df0c71b] benjamin@bengfort.com $

"""
Testing for the text helpers library.
"""

##########################################################################
## Imports
##########################################################################

import unittest

from baleen.exceptions import ExportError
from baleen.utils.text import sanitize_html, RAW, SAFE, TEXT


class SanitizeHtmlTests(unittest.TestCase):
    """ Tests the exporter's HTML sanitize methods """

    @classmethod
    def setUpClass(cls):
        cls.sample_html = ('<html>'
                           '<head><script>javascript here</script></head>'
                           '<body><b>body &amp;\n mind</b></body>'
                           '</html>')

    @classmethod
    def tearDownClass(self):
        """
        Drop the mongomock connection
        """
        pass

    def test_sanitize_requires_a_valid_level(self):
        """  Sanitize_html requires a supported level """
        with self.assertRaises(ValueError):
            sanitize_html(self.sample_html, "bogus")

    def test_sanitize_returns_input_for_level_none(self):
        """  sanitize_html returns unmodified input for level None """
        self.assertEqual(sanitize_html(self.sample_html, None), self.sample_html)

    def test_sanitize_raw(self):
        """  Sanitize level raw returns the content as submitted """
        self.assertEqual(sanitize_html(self.sample_html, RAW), self.sample_html)

    def test_sanitize_raw_handles_none(self):
        """
        Sanitize level raw accepts None gracefully
        """
        self.assertEqual(sanitize_html(None, RAW), None)

    def test_sanitize_safe(self):
        """  Sanitize level safe applies Readability and returns the body """

        # Give Readability a simpler HTML sample to keep its parse strategy simple
        sample_html = ('<html>'
                       '<head><script>javascript here</script></head>'
                       '<body>body</body>'
                       '</html>')
        expected = '<body id="readabilityBody">body</body>'
        self.assertEqual(sanitize_html(sample_html, SAFE), expected)

    def test_sanitize_safe_handles_none(self):
        """
        Sanitize level safe accepts None gracefully
        """
        self.assertEqual(sanitize_html(None, SAFE), None)

    def test_sanitize_text(self):
        """
        Sanitize level text strips HTML tags, removes newlines,
         and converts the html entity ampersand into an ampersand character
        """
        expected = 'body & mind'
        self.assertEqual(sanitize_html(self.sample_html, TEXT), expected)

    def test_sanitize_text_handles_none(self):
        """
        Sanitize level text accepts None gracefully
        """
        self.assertEqual(sanitize_html(None, TEXT), None)
