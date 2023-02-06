from datetime import datetime
from deletetweets.utils import parse_date
from deletetweets.tweet import Tweet

OFFSET = len('window.YTD.tweets.part0 = ')-1


class TweetReader():
    def __init__(self, rows, params):
        self.rows = rows
        self.since_date = datetime.min if params.since_date is None else parse_date(params.since_date)
        self.until_date = datetime.now() if params.until_date is None else parse_date(params.until_date)
        self.filters = params.filters
        self.spare_ids = params.spare_ids
        self.min_likes = 0 if params.min_likes is None else params.min_likes
        self.min_retweets = 0 if params.min_retweets is None else params.min_retweets

        self.total = 0
        self.deleted = 0
        self.skipped = 0

    def process(self):
        for row in self.rows:
            self.total += 1
            tweet = Tweet(row)

            if tweet.created_at >= self.until_date or tweet.created_at <= self.since_date:
                self.skipped += 1
                continue

            if 'retweets' in self.filters and not tweet.is_retweet():
                self.skipped += 1
                continue

            if 'replies' in self.filters and not tweet.is_reply():
                self.skipped += 1
                continue

            if tweet.id_str in self.spare_ids:
                self.skipped += 1
                continue

            if tweet.has_minimum('favorite_count', self.min_likes):
                self.skipped += 1
                continue

            if tweet.has_minimum('retweet_count', self.min_retweets):
                self.skipped += 1
                continue

            yield tweet
