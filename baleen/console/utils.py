# baleen.console.utils
# Argparse extensions and utilities.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 11:01:35 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: baleen.console.utils.py [] benjamin@bengfort.com $

"""
Argparse extensions and utilities.
"""

##########################################################################
## Imports
##########################################################################

import argparse


##########################################################################
## Console Parsers
##########################################################################

def csv(type=int):
    """
    Argparse type for comma seperated values. Also parses the type, e.g. int.
    """
    def parser(s):
        try:
            parse = lambda p: type(p.strip())
            return map(parse, s.split(","))
        except Exception as e:
            raise argparse.ArgumentTypeError(
                "Could not parse CSV value to type {}: {!r}".format(type.__name__, s)
            )

    return parser
