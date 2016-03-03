# baleen.console.commands.export
# Export utility to dump an HTML corpus to disk from the database.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 11:12:50 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: export.py [] benjamin@bengfort.com $

"""
Export utility to dump an HTML corpus to disk from the database.
"""

##########################################################################
## Imports
##########################################################################

import os
import baleen.models as db

from commis import Command
from baleen.config import settings
from baleen.console.utils import csv
from baleen.export import MongoExporter

##########################################################################
## Command
##########################################################################

class ExportCommand(Command):

    name = 'export'
    help = 'Export the raw HTML corpus for doing NLP'
    args = {
        ('-C', '--categories'): {
            'type': csv(str),
            'default': None,
            'help': 'Specify categories to export',
        },
        'location': {
            'nargs': 1,
            'type': str,
            'help': 'Location to write the corpus out to'
        }
    }

    def handle(self, args):
        # Connect to database
        db.connect()

        # Export from the database
        exporter = MongoExporter()
        exporter.export(args.location[0], categories=args.categories)

        # Perform counts of export
        root = args.location[0]
        cats = filter(
            os.path.isdir, [os.path.join(root, cat) for cat in os.listdir(root)]
        )
        docs = sum(len(os.listdir(d)) for d in cats)

        return (
            "Exported {} documents in {} categories "
            "as well as a readme to {}.".format(
                docs, len(cats), root
            )
        )
