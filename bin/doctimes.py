#!/usr/bin/env python
# export publish dates of documents in the corpus.

import os
import csv
import bson
import argparse

from datetime import datetime
from pymongo import MongoClient


def main(args):

    # Connect to the Database
    conn = MongoClient()
	db = conn.baleen
	posts = db.posts

    # Create a hook to the CSV file
    writer = csv.DictWriter(args.outpath, fieldnames=["_id", "pubdate"])
    writer.writeheader()

    # Collect the IDs and pubdates
    count = 0
    for row in posts.find({}, {"_id": 1, "pubdate": 1}):
        count += 1
        writer.writerow(row)

    print("wrote {} rows to {}".format(count, args.outpath.name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="export pubdates for documents by id"
    )

    parser.add_argument(
        "-o", "--outpath", default="pubdates.csv", type=argparse.FileType('w'),
        help="location to write out the results csv file to",
    )

    args = parser.parse_args()
    main(args)
