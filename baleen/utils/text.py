# baleen.utils.text
# Utility functions for Baleen
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat Jun 03 18:48:00 2017 -0400
#
# Copyright (C) 2017 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: text.py [caaaaca] benjamin@bengfort.com $

"""
Text-related Utility functions for Baleenc
"""

##########################################################################
## Imports
##########################################################################

import bleach
from readability.readability import Document

##########################################################################
## Constants
##########################################################################

RAW = 'raw'
SAFE = 'safe'
TEXT = 'text'
SANITIZE_LEVELS = (RAW, SAFE, TEXT)


def get_raw_html(html):
    """
    :param html: html content
    :return: the unmodified html
    """
    return html


def get_safe_html(html):
    """
    Applies Readability's sanitize() method to content.
    :param html: the content to sanitize
    :return: the body of the html content minus html tags
    """
    if html is None:
        return None
    return Document(html).summary()


def get_text_from_html(html):
    """
    Applies the 'safe' level of sanitization, removes newlines,
    and converts the html entity for ampersand into the ampersand character.
    :param html: the content to sanitize
    :return: sanitized content
    """
    if html is None:
        return html

    text = get_safe_html(html)
    text = bleach.clean(text, tags=[], strip=True)
    text = text.strip()
    text = text.replace("\n", "")
    text = text.replace("&amp;", "&")
    return text


def sanitize_html(html, level):
    """
    Return a sanitized version of html content
    :param html: the content to sanitized
    :param level: the type of sanitization - one of ['raw', 'safe', 'text', None]
    :return: sanitized content
    """
    if level == SAFE:
        return get_safe_html(html)
    elif level == RAW:
        return get_raw_html(html)
    elif level == TEXT:
        return get_text_from_html(html)
    elif level is None:
        return html

    raise ValueError(
        "{level} is not a supported sanitize_html level.".format(
            level=level
        )
    )
