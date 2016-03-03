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
from commis.exceptions import ConsoleError
from baleen.ingest import Ingestor, MongoIngestor, OPMLIngestor

##########################################################################
## Command
##########################################################################

class IngestCommand(Command):

    name = 'ingest'
    help = 'Ingests the RSS feeds to MongoDB'
    args = {
        '--opml': {
            'type': str,
            'default': None,
            'help': 'Ingest directly from an OPML file',
        },
        'feeds': {
            'type': str,
            'nargs': "*",
            'default': None,
            'metavar': 'URL',
            'help': 'Specify a list of feeds as urls'
        }
    }

    def handle(self, args):

        ingestor = MongoIngestor()

        if args.opml:
            ingestor = OPMLIngestor(args.opml)
            raise ConsoleError("opml ingestion is an untested utility!")

        if args.feeds:
            ingestor = Ingestor(args.feeds)
            raise ConsoleError("feed ingestion is an untested utility!")

        db.connect()
        ingestor.ingest()
        return (
            "Processed {feeds} feeds ({timer}): "
            "{posts} posts with {errors} errors"
        ).format(
            timer=ingestor.timer, **ingestor.counts
        )
