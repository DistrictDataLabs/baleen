# baleen
# An automated ingestion service for blogs to construct a corpus.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Sep 19 10:55:58 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
An automated ingestion service for blogs to construct a corpus for NLP
research.
"""

##########################################################################
## Imports
##########################################################################



##########################################################################
## Vesioning
##########################################################################

__version__ = (0,1,0)

def get_version():
    """
    Returns the string containing the version number
    """
    return "%i.%i.%i" % __version__
