# baleen.models
# Object Document Models for use with Mongo and mongoengine
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Sep 19 11:30:53 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: models.py [] benjamin@bengfort.com $

"""
Object Document Models for use with Mongo and mongoengine
"""

##########################################################################
## Imports
##########################################################################

import hashlib
import mongoengine as me

from datetime import datetime
from baleen.config import settings

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
    name = kwargs.get('name', settings.database.name)
    host = kwargs.get('host', settings.database.host)
    port = kwargs.get('port', settings.database.port)

    return me.connect(name, host=host, port=port)

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
        return self.urls.get('htmlurl')

    def __unicode__(self):
        return self.title

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
        Returns an HTML string of the content of the Post
        """

        template = (
            u"<!doctype html>\n"
            u"<html>\n"
            u"<head>\n\t<meta charset=\"utf-8\"\n>"
            u"\t<title>%s</title>\n</head>\n"
            u"<body>\n\n%s\n\n</body>\n</html>\n"
        )

        return template % (self.title, self.content)

    def __unicode__(self):
        return self.title

##########################################################################
## Signals
##########################################################################

me.signals.pre_save.connect(Feed.pre_save, sender=Feed)
me.signals.pre_save.connect(Post.pre_save, sender=Post)
