# baleen.console.commands.serve
# Run a local development version of the Baleen Flask app.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Apr 07 08:05:34 2016 -0400
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: serve.py [] benjamin@bengfort.com $

"""
Run a local development version of the Baleen Flask app.
"""

##########################################################################
## Imports
##########################################################################

from commis import Command
from baleen.www.app import app
from baleen.config import settings

##########################################################################
## Command
##########################################################################

class ServeCommand(Command):

    name = 'serve'
    help = 'serve the Flask administration application'
    args = {
        '--host': {
            'metavar': 'ADDR',
            'default': settings.server.host,
            'help': 'set the host to run the app on'
        },
        '--port': {
            'metavar': 'PORT',
            'type': int,
            'default': settings.server.port,
            'help': 'set the port to run the app on'
        },
        '--debug': {
            'action': 'store_true',
            'help': 'force debug mode in Flask'
        }
    }

    def handle(self, args):
        """
        Runs the Baleen Flask application.
        """
        kwargs = {
            'host': args.host,
            'port': args.port,
            'debug': args.debug or settings.debug,
        }

        app.run(**kwargs)
        return " * Web application stopped"
