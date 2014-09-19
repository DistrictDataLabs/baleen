#!/usr/bin/env python
# setup
# Setup script for baleen
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Sep 19 10:59:24 2014 -0400
#
# Copyright (C) 2014 District Data Labs
# For license information, see LICENSE.txt and NOTICE.md
#
# ID: setup.py [] benjamin@bengfort.com $

"""
Setup script for baleen
"""

##########################################################################
## Imports
##########################################################################

try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    raise ImportError("Could not import \"setuptools\"."
                      "Please install the setuptools package.")

##########################################################################
## Package Information
##########################################################################

## Discover the packages
packages = find_packages(where=".", exclude=("tests", "bin", "docs", "fixtures",))

## Load the requirements
requires = []
with open('requirements.txt', 'r') as reqfile:
    for line in reqfile:
        requires.append(line.strip())

## Define the classifiers
classifiers = (
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
)

## Define the keywords
keywords = ('nlp', 'baleen', 'ingestion', 'blogs', 'rss')

## Define the configuration
config = {
    "name": "baleen",
    "version": "0.1.0",
    "description": "An automated ingestion service for blogs to construct a corpus for NLP research.",
    "license": "MIT",
    "author": "Benjamin Bengfort",
    "author_email": "benjamin@bengfort.com",
    "url": "https://github.com/bbengfort/baleen",
    "download_url": 'https://github.com/bbengfort/baleen/tarball/v0.1.0',
    "packages": packages,
    "install_requires": requires,
    "classifiers": classifiers,
    "keywords": keywords,
    "zip_safe": True,
    "scripts": ['bin/baleen'],
}

##########################################################################
## Run setup script
##########################################################################

if __name__ == '__main__':
    setup(**config)
