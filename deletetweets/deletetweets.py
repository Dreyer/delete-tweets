import io
import os
import sys
import json

from twitter import Api as TwitterAPI, TwitterError, Status as TwitterStatus
from datetime import datetime
from deletetweets.utils import parse_date, log


class TweetDestroyer(object):
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


class Tweet():
    def __init__(self, row):
        if 'tweet' not in row:
            raise KeyError('Malformed row: %s' % str(row))

        tweet = row['tweet']
        param_defaults = TwitterStatus().param_defaults

        # Note: This parameter is in the Twitter archive
        # but not in the Twitter model for a Status.
        param_defaults['in_reply_to_user_id_str'] = None

        for (param, default) in param_defaults.items():
            setattr(self, param, tweet.get(param, default))

        # Coerce values to make it easier to compare.
        self.created_at = parse_date(self.created_at)

    def is_retweet(self):
        return self.full_text.startswith('RT @')

    def is_reply(self):
        return self.in_reply_to_user_id_str != ''

    def has_minimum(self, count_of, threshold=0):
        value = getattr(self, count_of, 0)
        return (threshold > 0 and value is not None and int(value) >= threshold)


class TweetReader(object):
    def __init__(self, rows, params):
        self.rows = rows
        self.since_date = datetime.min if params.since_date is None else parse_date(params.since_date)
        self.until_date = datetime.now() if params.until_date is None else parse_date(params.until_date)
        self.filters = params.filters
        self.spare_ids = params.spare_ids
        self.min_likes = 0 if params.min_likes is None else params.min_likes
        self.min_retweets = 0 if params.min_retweets is None else params.min_retweets

    def process(self):
        for row in self.rows:
            tweet = Tweet(row)

            if tweet.created_at >= self.until_date or tweet.created_at <= self.since_date:
                continue

            if 'retweets' in self.filters and not tweet.is_retweet():
                continue

            if 'replies' in self.filters and not tweet.is_reply():
                continue

            if tweet.id_str in self.spare_ids:
                continue

            if tweet.has_minimum('favorite_count', self.min_likes):
                continue

            if tweet.has_minimum('retweet_count', self.min_retweets):
                continue

            yield tweet


def delete(params):
    with io.open(params.file, mode="r", encoding="utf-8") as fp:
        count = 0

        api = TwitterAPI(consumer_key=os.environ["TWITTER_CONSUMER_KEY"],
                         consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
                         access_token_key=os.environ["TWITTER_ACCESS_TOKEN"],
                         access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
                         sleep_on_rate_limit=True)
        destroyer = TweetDestroyer(api, params.dry_run)

        data_raw = fp.read()
        offset = len("window.YTD.tweets.part0 = ")-1
        data_json = data_raw[offset:]

        rows = json.loads(data_json)
        reader = TweetReader(rows, params)

        for tweet in reader.process():
            destroyer.destroy(tweet.id_str)
            count += 1

        print("Number of deleted tweets: %s\n" % count)

    sys.exit()
