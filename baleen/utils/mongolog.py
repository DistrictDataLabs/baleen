# baleen.utils.mongolog
# Handlers and formatters for logging to Mongo
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue Sep 23 09:11:52 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: mongolog.py [] benjamin@bengfort.com $

"""
Handlers and formatters for logging to Mongo
"""

##########################################################################
## Imports
##########################################################################

import getpass
import logging
import logging.config
from baleen.utils.timez import *
from baleen.config import settings

from datetime import datetime
from socket import gethostname
from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError

##########################################################################
## Mongo Formatter/Handler
##########################################################################

class MongoFormatter(logging.Formatter):

    def __init__(self, fmt='%(name)s %(levelname)s [%(asctime)s] -- %(message)s', datefmt=COMMON_DATETIME):
        super(MongoFormatter, self).__init__(fmt, datefmt)

    def format(self, record):
        """
        Formats LogRecord into a Python dictionary
        """

        ## Get the dictionary ready for Mongo
        data    = record.__dict__.copy()

        ## Get the log message as intended via super
        message   = super(MongoFormatter, self).format(record)
        timestamp = datetime.fromtimestamp(data.pop('created'))
        location  = {
            'module': data.pop('module'),
            'file': data.pop('pathname'),
            'filename': data.pop('filename'),
            'lineno': data.pop('lineno'),
            'method': data.pop('funcName')
        }
        error     = {
            'info': data.pop('exc_info'),
            'text': data.pop('exc_text'),
        }
        process   = {
            'process': data.pop('process'),
            'processName': data.pop('processName'),
            'thread': data.pop('thread'),
            'threadName': data.pop('threadName'),
        }
        logger    = data.pop('name')
        level     = {
            'number': data.pop('levelno'),
            'name': data.pop('levelname'),
        }
        info      = tuple(unicode(arg) for arg in data.pop('args'))

        for key in ('relativeCreated', 'msecs', 'msg'):
            del data[key]

        data.update({
            'logger': logger,
            # 'process': process,
            'message': message,
            'timestamp': timestamp,
            'level': level,
            # 'location': location,
            'error': error,
            'user': getpass.getuser(),
            'host': gethostname(),
            # 'info': info,
        })

        return data

class MongoHandler(logging.Handler):

    def __init__(self, level=logging.NOTSET, **kwargs):
        super(MongoHandler, self).__init__(level)
        self.host            = kwargs.get('host', settings.database.host)
        self.port            = kwargs.get('port', settings.database.port)
        self.database_name   = kwargs.get('database', settings.database.name)
        self.collection_name = kwargs.get('collection', 'logs')
        self.fail_silently   = kwargs.get('fail_silently', False)
        self.formatter       = kwargs.get('formatter', MongoFormatter())

        self.connection      = None
        self.database        = None
        self.collection      = None
        self.connect()

    def connect(self):
        """
        Connect to the Mongo database.
        """
        try:
            self.connection = MongoClient(host=self.host, port=self.port)
        except PyMongoError:
            if self.fail_silently:
                return
            else:
                raise

        self.database   = self.connection[self.database_name]
        self.collection = self.database[self.collection_name]

    def close(self):
        """
        Close the connection to the Mongo database.
        """
        if self.connection is not None:
            self.connection = None

    def emit(self, record):
        """
        Insert log record into Mongo database
        """
        if self.collection is not None:
            try:
                self.collection.insert(self.format(record))
            except Exception:
                if not self.fail_silently:
                    self.handleError(record)

if __name__ == '__main__':
    logger = logging.getLogger('demo')
    logger.setLevel(logging.INFO)
    logger.addHandler(MongoHandler())
    logger.info("This is a test of the logging system")
