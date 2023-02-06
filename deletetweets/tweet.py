from twitter import Status as TwitterStatus
from deletetweets.utils import parse_date


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
