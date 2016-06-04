# baleen.version
# Stores version information such that it can be read by setuptools.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Feb 18 20:14:16 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: version.py [edff1dd] benjamin@bengfort.com $

"""
Stores version information such that it can be read by setuptools.
"""

##########################################################################
## Imports
##########################################################################

__version_info__ = {
    'major': 0,
    'minor': 3,
    'micro': 3,
    'releaselevel': 'final',
    'serial': 0,
}


def get_version(short=False,version_info=__version_info__):
    """
    Computes a string representation of the version from __version_info__.
    """
    assert version_info['releaselevel'] in ('alpha', 'beta', 'final')
    vers = ["%(major)i.%(minor)i" % version_info, ]
    if version_info['micro']:
        vers.append(".%(micro)i" % version_info)
    if version_info['releaselevel'] != 'final' and not short:
        vers.append('%s%i' % (version_info['releaselevel'][0],
                              version_info['serial']))
    return ''.join(vers)
