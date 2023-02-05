import io
import os
import sys
import json

import twitter
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
        except twitter.TwitterError as err:
            log(tweet_id, "Exception: %s\n" % err.message)


class TweetReader(object):
    def __init__(self, rows, params):
        self.rows = rows
        self.since_date = datetime.min if params.since_date is None else parse_date(params.since_date)
        self.until_date = datetime.now() if params.until_date is None else parse_date(params.until_date)
        self.filters = params.filters
        self.spare_ids = params.spare_ids
        self.min_likes = 0 if params.min_likes is None else params.min_likes
        self.min_retweets = 0 if params.min_retweets is None else params.min_retweets

    def read(self):
        for row in self.rows:
            if row["tweet"].get("created_at", "") != "":
                tweet_date = parse_date(row["tweet"]["created_at"])
                if tweet_date >= self.until_date or tweet_date <= self.since_date:
                    continue

            if ("retweets" in self.filters and
                    not row["tweet"].get("full_text").startswith("RT @")) or \
                    ("replies" in self.filters and
                     row["tweet"].get("in_reply_to_user_id_str") == ""):
                continue

            if row["tweet"].get("id_str") in self.spare_ids:
                continue

            if (self.min_likes > 0 and int(row["tweet"].get("favorite_count")) >= self.min_likes) or \
                    (self.min_retweets > 0 and int(row["tweet"].get("retweet_count")) >= self.min_retweets):
                continue

            yield row


def delete(params):
    with io.open(params.file, mode="r", encoding="utf-8") as fp:
        count = 0

        api = twitter.Api(consumer_key=os.environ["TWITTER_CONSUMER_KEY"],
                          consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
                          access_token_key=os.environ["TWITTER_ACCESS_TOKEN"],
                          access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
                          sleep_on_rate_limit=True)
        destroyer = TweetDestroyer(api, params.dry_run)

        data_raw = fp.read()
        offset = len("window.YTD.tweets.part0 = ")-1
        data_json = data_raw[offset:]

        rows = json.loads(data_json)
        for row in TweetReader(rows, params).read():
            destroyer.destroy(row["tweet"]["id_str"])
            count += 1

        print("Number of deleted tweets: %s\n" % count)

    sys.exit()
