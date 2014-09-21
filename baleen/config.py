# baleen.config
# Uses confire to get meaningful configurations from a yaml file
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Sep 19 11:14:33 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: config.py [] benjamin@bengfort.com $

"""
Uses confire to get meaningful configurations from a yaml file
"""

##########################################################################
## Imports
##########################################################################

import os
import confire

##########################################################################
## Configuration
##########################################################################

class MongoConfiguration(confire.Configuration):
    """
    Configuration for the Mongo database
    """

    host = "localhost"
    port = 27017
    name = "baleen"

class BaleenConfiguration(confire.Configuration):
    """
    Meaningful defaults and required configurations.

    debug:    the app will print or log debug statements
    testing:  the app will not overwrite important resources
    database: connection information for mongo
    """

    CONF_PATHS = [
        "/etc/baleen.yaml",                      # System configuration
        os.path.expanduser("~/.baleen.yaml"),    # User specific config
        os.path.abspath("conf/baleen.yaml"),     # Local configuration
    ]

    debug    = True
    testing  = True
    database = MongoConfiguration()


## Load settings immediately for import
settings = BaleenConfiguration.load()

if __name__ == '__main__':
    print settings
