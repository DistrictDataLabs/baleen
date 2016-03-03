# baleen.console.commands.summary
# A utility to print out information about the Baleen state.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 11:08:57 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: summary.py [] benjamin@bengfort.com $

"""
A utility to print out information about the Baleen state.
"""

##########################################################################
## Imports
##########################################################################

import baleen
import baleen.models as db

from commis import Command
from baleen.config import settings

##########################################################################
## Command
##########################################################################

class SummaryCommand(Command):

    name = 'info'
    help = 'Print info about Baleen from the database'
    args = {
        ('-c', '--config'): {
            'action': 'store_true',
            'default': False,
            'help': 'Also print the configuration',
        }
    }

    def handle(self, args):
        # Setup output and connect to database.
        output = []
        db.connect()

        # Printout configuration details as necessary.
        if args.config:
            output.append(u"Configuration:")
            output.append(unicode(settings))
            output.append(u"")

        output.append(u"Baleen v{} Status:".format(baleen.get_version()))
        output.append(
            u"{} Feeds and {} Posts".format(
                db.Feed.objects.count(), db.Post.objects.count()
            )
        )

        latest = db.Feed.objects.order_by('-updated').first()
        output.extend([
            u"",
            u"Latest Feed: ",
            u"    Title: \"{}\"".format(latest.title),
            u"    eTag: \"{}\"".format(latest.etag),
            u"    Modified: {}".format(latest.modified),
            u"    Posts: {}".format(latest.count_posts())
        ])

        latest = db.Post.objects.order_by('-id').first()
        output.extend([
            u"",
            u"Latest Post: ",
            u"    Title: \"{}\"".format(latest.title),
            u"    Feed: \"{}\"".format(latest.feed.title),
            u"    Fetched: {}".format(latest.created.strftime("%Y-%m-%d %H:%M:%S"))
        ])

        return u"\n".join(output).encode('utf-8', errors='replace')
