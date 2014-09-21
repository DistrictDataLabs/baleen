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

from baleen.config import settings

##########################################################################
## Module Constants
##########################################################################

FEEDTYPES = (
    'rss',
    'atom',
    'xml',
    'json'
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

class Feed(me.Document):

    type      = me.StringField( required=True, choices=FEEDTYPES, default="rss")
    title     = me.StringField( max_length=256 )
    xmlurl    = me.URLField( required=True, unique=True )
    htmlurl   = me.URLField()
    category  = me.StringField( required=True )


    meta      = {
        'collection': 'feeds',
    }

class Post(me.Document):

    feed      = me.ReferenceField(Feed)
    title     = me.StringField( max_length=512 )
    url       = me.URLField( required=True, unique=True )
    pubdate   = me.DateTimeField()
    content   = me.StringField( required=True )
    signature = me.StringField( required=True, max_length=64, min_length=64, unique=True )

    meta      = {
        'collection': 'posts',
    }

    def hash(self):
        """
        Returns the SHA256 hash of the content.
        """
        sha = hashlib.sha256()
        sha.update(self.content)
        return sha.hexdigest()

    def save(self, *args, **kwargs):
        if not self.signature:
            self.signature = self.hash()
        return super(Post, self).save(*args, **kwargs)
