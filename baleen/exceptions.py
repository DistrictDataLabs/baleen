# baleen.exceptions
# Exceptions hierarchy for the Baleen module.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 13:59:03 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: exceptions.py [] benjamin@bengfort.com $

"""
Exceptions hierarchy for the Baleen module.
"""

##########################################################################
## Exceptions Hierarchy
##########################################################################

class BaleenError(Exception):
    """
    The root of all errors in Baleen (hopefully)
    """
    pass


class FeedTypeError(BaleenError):
    """
    Could not detect the feed type for synchronization
    """
    pass


class IngestionError(BaleenError):
    """
    Something went wrong specifically with the ingestion process
    """
    pass


class SynchronizationError(IngestionError):
    """
    Something went wrong with feed synchronization
    """
    pass


class WranglingError(IngestionError):
    """
    Something went wrong wrangling a post
    """
    pass


class FetchError(WranglingError):
    """
    Could not fetch the webpage for the post
    """
    pass
