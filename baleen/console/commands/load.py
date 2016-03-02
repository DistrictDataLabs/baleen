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
from baleen.opml import ingest as load_opml

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
        count = 0
        for path in args.opml:
            count += load_opml(path)
        return "Ingested %i feeds from %i OPML files" % (count, len(args.opml))
