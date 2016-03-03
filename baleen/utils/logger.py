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
import getpass
import warnings
import logging.config

from baleen.config import settings
from baleen.utils.timez import COMMON_DATETIME

##########################################################################
## Logging configuration
##########################################################################

configuration = {
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

logging.config.dictConfigClass(configuration).configure()
if not settings.debug: logging.captureWarnings(True)

##########################################################################
## Logger utility
##########################################################################

class WrappedLogger(object):
    """
    Wraps the Python logging module's logger object to ensure that all baleen
    logging happens with the correct configuration as well as any extra
    information that might be required by the log file (for example, the user
    on the machine, hostname, IP address lookup, etc).

    Subclasses must specify their logger as a class variable so all instances
    have access to the same logging object.
    """

    logger = None

    def __init__(self, **kwargs):
        self.raise_warnings = kwargs.pop('raise_warnings', settings.debug)
        self.logger = kwargs.pop('logger', self.logger)

        if not self.logger or not hasattr(self.logger, 'log'):
            raise TypeError(
                "Subclasses must specify a logger, not {}"
                .format(type(self.logger))
            )

        self.extras = kwargs

    def log(self, level, message, *args, **kwargs):
        """
        This is the primary method to override to ensure logging with extra
        options gets correctly specified.
        """
        extra = self.extras.copy()
        extra.update(kwargs.pop('extra', {}))

        kwargs['extra'] = extra
        self.logger.log(level, message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        return self.log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        return self.log(logging.INFO, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        """
        Specialized warnings system. If a warning subclass is passed into
        the keyword arguments and raise_warnings is True - the warnning will
        be passed to the warnings module.
        """
        warncls = kwargs.pop('warning', None)
        if warncls and self.raise_warnings:
            warnings.warn(message, warncls)

        return self.log(logging.WARNING, message, *args, **kwargs)

    # Alias warn to warning
    warn = warning

    def error(self, message, *args, **kwargs):
        return self.log(logging.ERROR, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        return self.log(logging.CRITICAL, message, *args, **kwargs)


##########################################################################
## The Ingestion Logger Class
##########################################################################

class IngestLogger(WrappedLogger):
    """
    Performs logging for the baleen process with the log options above.
    """

    logger = logging.getLogger('baleen.ingest')

    def __init__(self, **kwargs):
        self._user = kwargs.pop('user', None)
        super(IngestLogger, self).__init__(**kwargs)

    @property
    def user(self):
        if not self._user:
            self._user = getpass.getuser()
        return self._user

    def log(self, level, message, *args, **kwargs):
        """
        Provide current user as extra context to the logger
        """
        extra = kwargs.pop('extra', {})
        extra.update({
            'user': self.user
        })

        kwargs['extra'] = extra
        super(IngestLogger, self).log(level, message, *args, **kwargs)


##########################################################################
## Logging Mixin
##########################################################################

class LoggingMixin(object):
    """
    Mix in to classes that need their own logging object!
    """

    @property
    def logger(self):
        """
        Instantiates and returns a IngestLogger instance
        """
        if not hasattr(self, '_logger') or not self._logger:
            self._logger = IngestLogger()
        return self._logger
