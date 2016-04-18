# baleen.models
# Object Document Models for use with Mongo and mongoengine
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Sep 19 11:30:53 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: models.py [5b443de] benjamin@bengfort.com $

"""
Object Document Models for use with Mongo and mongoengine
"""

##########################################################################
## Imports
##########################################################################

import baleen
import hashlib
import mongoengine as me

from datetime import datetime,timedelta
from baleen.config import settings
from baleen.utils.timez import humanizedelta


##########################################################################
## Module Constants
##########################################################################

FEEDTYPES = (
    'atom',
    'atom01',
    'atom02',
    'atom03',
    'atom10',
    'cdf',
    'rss',
    'rss090',
    'rss091n',
    'rss092',
    'rss093',
    'rss094',
    'rss10',
    'rss20',
)

##########################################################################
## Helper Functions
##########################################################################

def connect(**kwargs):
    """
    Wrapper for mongoengine connect - connects with configuration details.
    """
    name = kwargs.pop('name', settings.database.name)
    host = kwargs.pop('host', settings.database.host)
    port = kwargs.pop('port', settings.database.port)

    return me.connect(name, host=host, port=port, **kwargs)

##########################################################################
## Models
##########################################################################

class Feed(me.DynamicDocument):

    version   = me.StringField(choices=FEEDTYPES)
    etag      = me.StringField()
    modified  = me.StringField()
    title     = me.StringField(max_length=256)
    link      = me.URLField(required=True, unique=True)
    urls      = me.DictField()
    category  = me.StringField(required=True)
    active    = me.BooleanField(default=True)
    fetched   = me.DateTimeField(default=None)
    created   = me.DateTimeField(default=datetime.now, required=True)
    updated   = me.DateTimeField(default=datetime.now, required=True)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.updated = datetime.now()

    meta      = {
        'collection': 'feeds',
    }

    @property
    def xmlurl(self):
        return self.link

    @property
    def htmlurl(self):
        return self.urls.get('htmlUrl')

    def count_posts(self):
        """
        Count the number of associated posts

        TODO: This is very, very slow on Mongo (fix and make better).
        """
        return Post.objects(feed=self).count()

    def __unicode__(self):
        return self.title if self.title else self.link

class Post(me.DynamicDocument):

    feed      = me.ReferenceField(Feed)
    title     = me.StringField( max_length=512 )
    url       = me.URLField( required=True, unique=True )
    pubdate   = me.DateTimeField()
    content   = me.StringField( required=True )
    tags      = me.ListField(me.StringField(max_length=256))
    signature = me.StringField( required=True, max_length=64, min_length=64, unique=True )
    created   = me.DateTimeField(default=datetime.now, required=True)
    updated   = me.DateTimeField(default=datetime.now, required=True)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.updated   = datetime.now()
        document.signature = document.hash()

    meta      = {
        'collection': 'posts',
    }

    def hash(self):
        """
        Returns the SHA256 hash of the content.
        """
        sha = hashlib.sha256()
        sha.update(self.content.encode('UTF-8'))
        return sha.hexdigest()

    def htmlize(self):
        """
        Returns an HTML string of the content of the Post.
        In the future we may use bleach to do sanitization or other simple
        sanity checks to ensure that things are going ok, which is why this
        method stub exists. 
        """
        return self.content

    def __unicode__(self):
        return self.title if self.title else self.url


class Job(me.DynamicDocument):

    jobid     = me.UUIDField(binary=False, required=True)
    name      = me.StringField(max_length=128, default="Unknown")
    failed    = me.BooleanField(default=False)
    reason    = me.StringField(max_length=512)
    version   = me.StringField(max_length=10, default=baleen.get_version)
    started   = me.DateTimeField(default=datetime.now, required=True)
    finished  = me.DateTimeField(default=None)
    updated   = me.DateTimeField(default=datetime.now, required=True)
    errors    = me.MapField(field=me.IntField())
    counts    = me.MapField(field=me.IntField())
    totals    = me.MapField(field=me.IntField())

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.updated = datetime.now()

    meta      = {
        'collection': 'jobs',
    }

    def duration(self, humanize=False):
        """
        Returns the timedelta of the duration.
        """
        finished = self.finished or datetime.now()
        delta = finished - self.started

        if humanize:
            return humanizedelta(
                days=delta.days,
                seconds=delta.seconds,
                microseconds=delta.microseconds
            )
        return delta

    @property
    def bootstrap_class(self):
        """
        Uses the duration to determine the colorization of the job.
        """
        if self.finished and self.failed:
            return "danger"

        if self.finished and not self.failed:
            if self.duration() > timedelta(minutes=30):
                return "warning"
            return "success"

        if not self.finished:

            if self.duration() < timedelta(minutes=30):
                return "success"

            elif timedelta(minutes=30) < self.duration() < timedelta(hours=2):
                return "warning"

            else:
                return "danger"

        return ""

    def __unicode__(self):
        return "{} Job {}".format(self.name, self.jobid)


class Log(me.DynamicDocument):

    level     = me.DictField()
    message   = me.StringField(max_length=4096)
    host      = me.StringField(max_length=255)
    user      = me.StringField(max_length=255)
    error     = me.DictField()
    logger    = me.StringField(max_length=255)
    asctime   = me.StringField(max_length=64)
    timestamp = me.DateTimeField()

    meta      = {
        'collection': 'logs',
    }

    @property
    def bootstrap_class(self):
        """
        Uses the log level to determine the bootstrap class.
        """
        levels = {
            "DEBUG": "success",
            "INFO": "info",
            "WARNING": "warning",
            "WARN": "warning",
            "ERROR": "danger",
            "CRITICAL": "danger",
        }

        key = self.level.get('name')
        if key and key in levels:
            return levels[key]
        return ""

    def __unicode__(self):
        return self.message

##########################################################################
## Signals
##########################################################################

me.signals.pre_save.connect(Feed.pre_save, sender=Feed)
me.signals.pre_save.connect(Post.pre_save, sender=Post)
me.signals.pre_save.connect(Post.pre_save, sender=Post)
