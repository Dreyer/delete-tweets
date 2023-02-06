#!/usr/bin/env python

import argparse
import os
import sys

from deletetweets import deletetweets

from dotenv import load_dotenv
load_dotenv()


def main():
    parser = argparse.ArgumentParser(description='Delete old tweets.')
    parser.add_argument('--since', dest='since_date', help='Delete tweets since this date', default=None)
    parser.add_argument('--until', dest='until_date', help='Delete tweets until this date', default=None)
    parser.add_argument('--filter', action='append', dest='filters', choices=['replies', 'retweets'],
                        help='Filter replies or retweets', default=[])
    parser.add_argument('--file', help='Path to the tweet.js file',
                        type=str, default='twitter-archive/data/tweets.js')
    parser.add_argument('--spare-ids', dest='spare_ids', help='A list of tweet ids to spare',
                        type=str, nargs='+', default=[])
    parser.add_argument('--spare-min-likes', dest='min_likes',
                        help='Spare tweets with more than the provided likes', type=int, default=0)
    parser.add_argument('--spare-min-retweets', dest='min_retweets',
                        help='Spare tweets with more than the provided retweets', type=int, default=0)
    parser.add_argument('--dry-run', dest='dry_run', action='store_true', default=False)
    parser.add_argument('--disable-cache', dest='disable_cache',
                        help='Disable caching of tweets', action='store_true', default=False)

    args = parser.parse_args()

    if not ('TWITTER_CONSUMER_KEY' in os.environ and
            'TWITTER_CONSUMER_SECRET' in os.environ and
            'TWITTER_ACCESS_TOKEN' in os.environ and
            'TWITTER_ACCESS_TOKEN_SECRET' in os.environ):
        sys.stderr.write("Twitter API credentials not set.\n")
        exit(1)

    if not os.path.isfile(args.file):
        sys.stderr.write("File for tweet.js not found at %s.\n" % args.file)
        exit(1)

    deletetweets.delete(args)


if __name__ == '__main__':
    main()
