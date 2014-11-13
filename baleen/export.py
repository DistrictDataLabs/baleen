# baleen.export
# Export an HTML corpus for analyses with NLTK
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Oct 03 16:49:20 2014 -0400
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: export.py [] benjamin@bengfort.com $

"""
Export an HTML corpus for analyses with NLTK
"""

##########################################################################
## Imports
##########################################################################

import os
import codecs

from datetime import datetime
from baleen.models import Feed, Post

##########################################################################
## Exporter
##########################################################################

class MongoExporter(object):

    def __init__(self, categories=None):
        self.categories = categories

    @property
    def categories(self):
        if self._categories is None:
            self._categories = Feed.objects.distinct('category')
        return self._categories

    @categories.setter
    def categories(self, value):
        self._categories = value

    def feeds(self, categories=None):
        """
        Returns a list of feeds for the specified categories
        """
        if isinstance(categories, basestring):
            categories = [categories]
        elif categories is None:
            categories = self.categories

        for category in categories:
            for feed in Feed.objects(category=category):
                yield feed

    def posts(self, categories=None):
        """
        Returns a set of posts for the given category
        """
        for feed in self.feeds(categories):
            for post in Post.objects(feed=feed):
                yield post

    def readme(self):
        """
        Returns a string with the README to write to disk
        """

        total  = 0
        counts = []

        for cat in self.categories:
            count = sum(1 for p in self.posts(cat))
            counts.append("   %s: %i posts" % (cat, count))
            total += count
        counts = "\n".join(counts)

        return (
            "Baleen RSS Export\n"
            "=================\n\n"
            "These feeds were exported on %s\n\n"
            "There are %i posts in %i categories in this corpus as follows:\n%s\n"
        ) % (
            datetime.now().strftime("%b %d, %Y at %H:%M"),
            total,
            len(self.categories),
            counts
        )

    def export(self, root, categories=None):
        """
        In the root directory writes each file and a README
        """

        if not os.path.exists(root):
            os.mkdir(root)

        if not os.path.isdir(root):
            raise Exception("%s is not a directory!" % root)

        for category in self.categories:
            dirname = os.path.join(root, category.replace(" ", "_"))
            if not os.path.exists(dirname):
                os.mkdir(dirname)

            for idx, post in enumerate(self.posts(category)):
                name = os.path.join(dirname, "%03i.html" % idx)
                with codecs.open(name, 'wb', encoding='utf8') as f:
                    f.write(post.htmlize())

        readme = os.path.join(root, "README")
        with codecs.open(readme, 'wb', encoding='utf8') as f:
            f.write(self.readme())

if __name__ == '__main__':
    from baleen.models import connect
    connect()
    exporter = MongoExporter()
    exporter.export('fixtures/corpus')

