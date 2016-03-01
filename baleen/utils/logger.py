# baleen.utils.logger
# Logging utility for Baleen
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Sep 22 15:47:34 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: logger.py [] benjamin@bengfort.com $

"""
Logging utility for Baleen
"""

##########################################################################
## Imports
##########################################################################

import logging
import logging.config
from baleen.utils.timez import *
from baleen.config import settings

##########################################################################
## Logging configuration
##########################################################################

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(name)s %(levelname)s [%(asctime)s] -- %(message)s',
            'datefmt': COMMON_DATETIME,
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': settings.logfile,
            'maxBytes': '536870912', # 512 MB
            'formatter': 'simple',
        },
        'mongolog': {
            'level': 'INFO',
            'class': 'baleen.utils.mongolog.MongoHandler',
        }
    },
    'loggers': {
        'baleen': {
            'level': settings.loglevel,
            'handlers': ['logfile'],
            'propagagte': True,
        },
        'baleen.ingest': {
            'level': 'INFO',
            'handlers': ['logfile', 'mongolog'],
            'propagate': False,
        }
    },
}

# SET LOGGING CONFIG HERE!!
logging.config.dictConfigClass(DEFAULT_LOGGING).configure()

##########################################################################
## Logger Class
##########################################################################

class Logger(object):
    """
    Helper class for performing logging with the correct configuration,
    and also ensures that the log configuration is imported. Subclasses
    must specify their logger as a class variable so that all instances
    have access to the same log.
    """

    logger = logging.getLogger('baleen')

    def __init__(self, **kwargs):
        self.logger = kwargs.pop('logger', self.logger)
        if not self.logger or not hasattr(self.logger, 'log'):
            raise NotImplementedError("Subclasses must specify a logger.")

        self.extras = kwargs

    def log(self, level, message, *args, **kwargs):
        """
        Subclasses may override this to ensure proper logging with extra
        options gets correctly specified. See the `ApacheLogger` for more
        information on how to specify Common Log format.
        """
        extra = kwargs.pop('extra', {})
        extra.update(self.extras)
        kwargs['extra'] = extra
        self.logger.log(level, message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        return self.log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        return self.log(logging.INFO, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        return self.log(logging.WARNING, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        return self.log(logging.ERROR, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        return self.log(logging.CRITICAL, message, *args, **kwargs)


class IngestLogger(Logger):
    """
    Performs logging for the baleen process with the log options above.
    """

    logger = logging.getLogger('baleen.ingest')
