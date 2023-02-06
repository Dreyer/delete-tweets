import io
import os
import sys
import json

from twitter import Api as TwitterAPI, TwitterError
from deletetweets.utils import log
from deletetweets.tweetreader import TweetReader, OFFSET


class TweetDestroyer():
    def __init__(self, twitter_api, dry_run=False):
        self.twitter_api = twitter_api
        self.dry_run = dry_run

    def destroy(self, tweet_id):
        try:
            if self.dry_run:
                log(tweet_id, 'Deleted Tweet (dry-run)')
            else:
                log(tweet_id, 'Deleted Tweet')
                self.twitter_api.DestroyStatus(tweet_id)
        except TwitterError as err:
            log(tweet_id, "Exception: %s\n" % err.message)


def delete(params):
    with io.open(params.file, mode='r', encoding='utf-8') as fp:
        api = TwitterAPI(consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
                         consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
                         access_token_key=os.environ['TWITTER_ACCESS_TOKEN'],
                         access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
                         sleep_on_rate_limit=True)
        destroyer = TweetDestroyer(api, params.dry_run)

        data_raw = fp.read()
        data_json = data_raw[OFFSET:]

        rows = json.loads(data_json)
        reader = TweetReader(rows, params)

        for tweet in reader.process():
            destroyer.destroy(tweet.id_str)
            if not params.dry_run:
                reader.deleted += 1

        print("Summary: Deleted %s of %s Tweets (Skipped: %s)\n" %
              (reader.deleted, reader.total, reader.skipped))

    sys.exit()
