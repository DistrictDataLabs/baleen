# baleen.console.commands.load
# Loads an OPML file from disk into the database.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 11:05:57 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: load.py [] benjamin@bengfort.com $

"""
Loads an OPML file from disk into the database.
"""

##########################################################################
## Imports
##########################################################################

from commis import Command
from baleen import models as db
from baleen.opml import load_opml

##########################################################################
## Command
##########################################################################

class LoadOPMLCommand(Command):

    name = 'load'
    help = 'Loads an OPML file from disk into the database.'
    args = {
        'opml': {
            'nargs': "+",
            'type': str,
            'help': 'OPML file(s) to import to the database'
        }
    }

    def handle(self, args):
        # Connect to the database
        db.connect()

        # Load the OPML files into the database
        count = sum(load_opml(path) for path in args.opml)
        return "Ingested {} feeds from {} OPML files".format(count, len(args.opml))
