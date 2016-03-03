# baleen.console.commands.run
# Runs the ingestor in the background every hour.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 11:14:25 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: run.py [] benjamin@bengfort.com $

"""
Runs the ingestor in the background every hour.
"""

##########################################################################
## Imports
##########################################################################

import time
import baleen
import schedule
import baleen.models as db

from commis import Command
from functools import partial
from baleen.ingest import MongoIngestor
from baleen.utils.logger import IngestLogger

##########################################################################
## Command
##########################################################################

class RunCommand(Command):

    name = 'run'
    help = 'Runs the ingest command every hour'
    args = {}

    def ingest(self, args):
        db.connect()
        ingestor = MongoIngestor()
        ingestor.ingest()

    def handle(self, args):
        logger = IngestLogger()
        logger.info(
            "Starting Baleen v{} ingestion service every hour.".format(baleen.get_version())
        )

        schedule.every().hour.do(partial(self.ingest, args))

        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                logger.info("Graceful shutdown of Baleen ingestion service.")
                return ""
            except Exception as e:
                logger.critical(str(e))
                return str(e)
