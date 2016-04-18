# baleen.console.commands.export
# Export utility to dump an HTML corpus to disk from the database.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 11:12:50 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: export.py [da54aa8] benjamin@bengfort.com $

"""
Export utility to dump an HTML corpus to disk from the database.
"""

##########################################################################
## Imports
##########################################################################

import os
import baleen.models as db

from commis import Command
from baleen.console.utils import csv
from baleen.export import MongoExporter, SCHEMES
from baleen.utils.timez import Timer

##########################################################################
## Command
##########################################################################

class ExportCommand(Command):

    name = 'export'
    help = 'export the raw HTML corpus for doing NLP'
    args = {
        '--list-categories': {
            'action': 'store_true',
            'default': False,
            'help': 'show the available categories and exit',
        },
        ('-C', '--categories'): {
            'type': csv(str),
            'default': None,
            'metavar': 'csv',
            'help': 'specify a list of categories to export',
        },
        ('-S', '--scheme'): {
            'type': str,
            'default': 'json',
            'choices': SCHEMES,
            'help': 'specify the output format for the corpus',
        },
        'location': {
            'nargs': 1,
            'type': str,
            'metavar': 'corpus directory',
            'help': 'location to write the corpus out to'
        },
    }

    def handle(self, args):
        # Connect to database
        db.connect()

        # Expand vars and user on the location passed
        root = os.path.expanduser(args.location[0])
        root = os.path.expandvars(root)

        # Create the exporter object
        exporter = MongoExporter(
            root, categories=args.categories, scheme=args.scheme
        )

        # If list categories is true, list them and exit.
        if args.list_categories:
            return "\n".join(sorted(exporter.categories))

        with Timer() as t:
            exporter.export()

        return (
            "Baleen corpus export complete in {}\n"
            "Exported {} posts in {} categories\n"
            "More information is in README in {}"
        ).format(
            t, sum(exporter.counts.values()),
            len(exporter.categories), root
        )
