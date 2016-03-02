# baleen.console.app
# Definition of the Baleen Utility app and commands
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 10:54:51 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: app.py [] benjamin@bengfort.com $

"""
Definition of the Baleen Utility app and commands
http://bbengfort.github.io/tutorials/2016/01/23/console-utility-commis.html
"""

##########################################################################
## Imports
##########################################################################

from commis import color
from commis import ConsoleProgram
from commis.exceptions import ConsoleError

from baleen.console.commands import *
from baleen.version import get_version

##########################################################################
## Utility Definition
##########################################################################

DESCRIPTION = "Management and administration commands for Baleen"
EPILOG      = "If there are any bugs or concerns, submit an issue on Github"
COMMANDS    = [
    IngestCommand,
    ExportCommand,
    LoadOPMLCommand,
    SummaryCommand,
    RunCommand,
]


##########################################################################
## The Baleen CLI Utility
##########################################################################

class BaleenUtility(ConsoleProgram):

    description = color.format(DESCRIPTION, color.CYAN)
    epilog      = color.format(EPILOG, color.MAGENTA)
    version     = color.format("baleen v{}", color.CYAN, get_version())

    @classmethod
    def load(klass, commands=COMMANDS):
        utility = klass()
        for command in commands:
            utility.register(command)
        return utility
