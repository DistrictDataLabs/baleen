#!/usr/bin/env python 

import sys
import argparse
import baleen.models as db


def posts(category):
    """
    Yields all posts from the MongoDB from the feeds with the specified category. 
    """
    for feed in db.Feed.objects(category=category):
        for post in db.Post.objects(feed=feed):
            yield post


def main(args):
    """
    Simple script that reads JSON data from mongo from a category, then dumps it out. 
    """
    db.connect() 
    for post in posts(args.category):
        args.output.write(post.to_json())
        args.output.write("\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser() 
    parser.add_argument('-o', '--output', default=sys.stdout, type=argparse.FileType('w'), help='location to write output to')
    parser.add_argument('-c', '--category', default='Politics', help='category to export the documents from') 

    args = parser.parse_args() 
    
    try:
        msg = main(args) 
        parser.exit(msg)
    except Exception as e:
        parser.error(str(e))

