#!/usr/bin/env python
# blaze
# A cleaning script that detects badly encoded Posts to eliminate.
#
# Author:   Benjamin Bengfort <bbengfort@districtdatalabs.com>
# Created:  Sat Aug 13 13:41:47 2016 -0400
#
# Copyright (C) 2016 District Data Labs
# For license information, see LICENSE.txt
#
# ID: blaze.py [] benjamin@bengfort.com $

"""
A cleaning script that detects badly encoded Posts to eliminate.
"""

##########################################################################
## Imports
##########################################################################

import os
import csv
import argparse
import baleen.models as db

from tqdm import tqdm
from baleen.utils.timez import Timer


##########################################################################
## Helper Functions
##########################################################################

def compile_object_ids(stream):
    """
    Creates a master list of object ids and writes them to a file.
    """

    items = db.Post.objects.count()
    query = db.Post.objects.scalar("id").no_dereference().no_cache()

    with tqdm(total=items, unit='id') as pbar:
        for idx, pid in enumerate(query):
            stream.write("{}\n".format(pid))
            pbar.update(1)

    return idx+1


def test_object_ids(pids, stream):
    """
    Given an iterable of pids, test it and write any bad ids to the fobj
    """
    errors = 0
    writer = csv.writer(stream)

    for pid in tqdm(pids, total=db.Post.objects.count(), unit='posts'):
        try:
            post = db.Post.objects.get(id=pid.strip())
        except Exception as e:
            writer.writerow([pid.strip(), str(e)])
            errors += 1

    return errors


if __name__ == "__main__":

    # Paths to various files on disk
    pids = os.path.join(os.getcwd(), "post_ids.txt")
    errs = os.path.join(os.getcwd(), "post_errs.csv")

    # Connect to the database
    db.connect()

    # Phase One: Write the Post IDs to a file.
    with open(pids, 'w') as f:
        with Timer() as timer:
            count = compile_object_ids(f)

    print("Phase One: wrote {} Posts IDs in {}".format(count, timer))

    # Phase Two: Check for errors
    with open(pids, 'r') as pidf:
        with open(errs, 'w') as errf:
            with Timer() as timer:
                errors = test_object_ids(pidf, errf)

    print("Phase Two: wrote {} Post errors in {}".format(errors, timer))

    # Optional: Remove the files that we have created
