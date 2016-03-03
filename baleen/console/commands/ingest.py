# baleen.console.commands.ingest
# Handles the ingestion utility both for OPML and feeds.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 10:58:56 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: ingest.py [] benjamin@bengfort.com $

"""
Handles the ingestion utility both for OPML and feeds.
"""

##########################################################################
## Imports
##########################################################################

import baleen.models as db

from commis import Command
# from baleen.feed import MongoFeedIngestor

##########################################################################
## Command
##########################################################################

class IngestCommand(Command):

    name = 'ingest'
    help = 'Ingests the RSS feeds to MongoDB'
    args = {
        ('-v', '--verbose'): {
            "action":"store_true",
            "default":False,
            "help":'Print details.',
        }
    }

    def handle(self, args):
        db.connect()
        ingestor = MongoFeedIngestor()
        ingestor.ingest(verbose=args.verbose)
        return ""
