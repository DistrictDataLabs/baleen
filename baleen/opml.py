# baleen.opml
# Reads opml files and gives back outline data
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat Sep 20 23:12:07 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: opml.py [] benjamin@bengfort.com $

"""
Reads opml files and gives back outline data
"""

##########################################################################
## Imports
##########################################################################

import baleen.models as db
from bs4 import BeautifulSoup
from collections import Counter
from mongoengine.errors import *

##########################################################################
## Load Database function
##########################################################################

def load_opml(path):
    """
    Loads an OPML file into the Mongo database; returns the count of the
    number of documents added to the database.
    """

    opml = OPML(path)
    rows = 0
    for feed in opml:
        feed.pop('type')                    # Unneeded for database
        feed.pop('text')                    # Unneeded for database
        feed['link'] = feed.pop('xmlUrl')   # Rename the XML URL
        feed['urls'] = {
            'xmlUrl':  feed['link'],        # Add xmlUrl to urls
            'htmlUrl': feed.pop('htmlUrl'), # Add htmlUrl to urls
        }
        feed = db.Feed(**feed)              # Construct without an ObjectId

        try:
            feed.save()
            rows += 1
        except NotUniqueError:
            continue
    return rows

##########################################################################
## OPMLReader
##########################################################################

class OPML(object):

    def __init__(self, path):
        """
        Reader for OPML XML files.
        """
        self.path = path

    def categories(self):
        """
        Reads the file to capture all the categories
        """
        with open(self.path, 'r') as data:
            soup = BeautifulSoup(data, 'xml')
            for topic in soup.select('body > outline'):
                yield topic['title']

    def counts(self):
        """
        Returns the counts of feeds in each category
        """
        counts = Counter()
        for item in self:
            counts[item['category']] += 1
        return counts

    def __iter__(self):
        """
        Yields a dictionary representing the attributes of the RSS feed
        from the OPML file; also captures category data.
        """
        with open(self.path, 'r') as data:
            soup = BeautifulSoup(data, 'xml')
            for topic in soup.select('body > outline'):
                for feed in topic.find_all('outline'):
                    data = feed.attrs.copy()
                    data['category'] = topic['title']
                    yield data

    def __len__(self):
        return sum(1 for item in self)

    def __str__(self):
        counts = self.counts()
        return "OPML with {} categories and {} feeds".format(
            len(counts), sum(counts.values())
        )

    def __repr__(self):
        return "<{} at {}>".format(self.__class__.__name__, self.path)
