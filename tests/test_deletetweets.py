from unittest import TestCase

from deletetweets.deletetweets import TweetReader, TweetDestroyer


class FakeArguments():
    def __init__(self, overrides=[]):
        self.since_date = None
        self.until_date = None
        self.filters = []
        self.file = "test-tweet.js"
        self.spare_ids = []
        self.min_likes = 0
        self.min_retweets = 0
        self.dry_run = False
        self.version = "0.0.0"

        if len(overrides) > 0:
            for (param, value) in overrides.items():
                setattr(self, param, value)


class FakeTwitterApi():
    def __init__(self):
        self.destroyed_tweets = []

    def DestroyStatus(self, tweet_id):
        self.destroyed_tweets.append(tweet_id)
        print("Destroyed tweet %s" % tweet_id)


class FakeReader():
    def __init__(self, test_dict):
        self.index = 0
        self.test_dict = test_dict

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.test_dict):
            raise StopIteration

        value = self.test_dict[self.index]
        self.index = self.index + 1
        return value

    def next(self):
        return self.__next__()


class TestDeleteTweets(TestCase):
    def test_tweet_destroyer_dry_run(self):
        mock_tweets = [{"tweet": {"id_str": "42", "full_text": ""}},
                       {"tweet": {"id_str": "43", "full_text": ""}},
                       {"tweet": {"id_str": "49", "full_text": ""}}]
        mock_args = FakeArguments({"dry_run": True})

        api = FakeTwitterApi()
        destroyer = TweetDestroyer(api, dry_run=True)

        rows = FakeReader(mock_tweets)
        tweets = TweetReader(rows, mock_args)

        for idx, val in enumerate(tweets.process()):
            destroyer.destroy(val["tweet"]["id_str"])

        self.assertEqual(len(api.destroyed_tweets), 0)

    def test_tweet_reader_retweet(self):
        mock_tweets = [{"tweet": {"id_str": "42", "full_text": "RT @github \\o/"}},
                       {"tweet": {"id_str": "43", "full_text": ""}},
                       {"tweet": {"id_str": "49", "full_text": ""}},
                       {"tweet": {"id_str": "44", "full_text": "RT @google OK, Google"}}]
        mock_args = FakeArguments({"filters": ["retweets"]})

        rows = FakeReader(mock_tweets)
        tweets = TweetReader(rows, mock_args)

        expected = [{"tweet": {"id_str": "42"}}, {"tweet": {"id_str": "44"}}]
        actual = []

        for idx, val in enumerate(tweets.process()):
            self.assertEqual(expected[idx]["tweet"]["id_str"], val["tweet"]["id_str"])
            actual.append(val)

        self.assertEqual(len(expected), len(actual))

    def test_tweet_reader_reply(self):
        mock_tweets = [{"tweet": {"id_str": "12", "in_reply_to_user_id_str": ""}},
                       {"tweet": {"id_str": "14", "in_reply_to_user_id_str": "200"}},
                       {"tweet": {"id_str": "16", "in_reply_to_user_id_str": ""}},
                       {"tweet": {"id_str": "18", "in_reply_to_user_id_str": "203"}}]
        mock_args = FakeArguments({"filters": ["replies"]})

        rows = FakeReader(mock_tweets)
        tweets = TweetReader(rows, mock_args)

        expected = [{"tweet": {"id_str": "14"}}, {"tweet": {"id_str": "18"}}]
        actual = []

        for idx, val in enumerate(tweets.process()):
            self.assertEqual(expected[idx]["tweet"]["id_str"], val["tweet"]["id_str"])
            actual.append(val)

        self.assertEqual(len(expected), len(actual))

    def test_tweet_reader_until_date(self):
        mock_tweets = [{"tweet": {"id_str": "21", "created_at": "Wed March 06 20:22:06 +0000 2013"}},
                       {"tweet": {"id_str": "22", "created_at": "Thu March 05 20:22:06 +0000 2014"}}]
        mock_args = FakeArguments({"until_date": "2014-02-01"})

        rows = FakeReader(mock_tweets)
        tweets = TweetReader(rows, mock_args)

        expected = [{"tweet": {"id_str": "21"}}]
        actual = []

        for idx, val in enumerate(tweets.process()):
            self.assertEqual(expected[idx]["tweet"]["id_str"], val["tweet"]["id_str"])
            actual.append(val)

        self.assertEqual(len(expected), len(actual))

    def test_tweet_reader_since_date(self):
        mock_tweets = [{"tweet": {"id_str": "23", "created_at": "Thu Apr 23 13:10:23 +0000 2020"}},
                       {"tweet": {"id_str": "24", "created_at": "Sat Apr 25 14:34:33 +0000 2020"}}]
        mock_args = FakeArguments({"since_date": "2020-04-24"})

        rows = FakeReader(mock_tweets)
        tweets = TweetReader(rows, mock_args)

        expected = [{"tweet": {"id_str": "24"}}]
        actual = []

        for idx, val in enumerate(tweets.process()):
            self.assertEqual(expected[idx]["tweet"]["id_str"], val["tweet"]["id_str"])
            actual.append(val)

        self.assertEqual(len(expected), len(actual))

    def test_tweet_reader_none_date(self):
        mock_tweets = [{"tweet": {"id_str": "21", "created_at": "Wed March 06 20:22:06 +0000 2013"}}]
        mock_args = FakeArguments()

        rows = FakeReader(mock_tweets)
        tweets = TweetReader(rows, mock_args)

        expected = [{"tweet": {"id_str": "21"}}]
        actual = []

        for idx, val in enumerate(tweets.process()):
            self.assertEqual(expected[idx]["tweet"]["id_str"], val["tweet"]["id_str"])
            actual.append(val)

        self.assertEqual(len(expected), len(actual))

    def test_tweet_reader_spare(self):
        mock_tweets = [{"tweet": {"id_str": "21"}},
                       {"tweet": {"id_str": "22"}},
                       {"tweet": {"id_str": "23"}}]
        mock_args = FakeArguments({"spare_ids": ["22", "23"]})

        rows = FakeReader(mock_tweets)
        tweets = TweetReader(rows, mock_args)

        expected = [{"tweet": {"id_str": "21"}}]
        actual = []

        for idx, val in enumerate(tweets.process()):
            self.assertEqual(expected[idx]["tweet"]["id_str"], val["tweet"]["id_str"])
            actual.append(val)

        self.assertEqual(len(expected), len(actual))

    def test_tweet_reader_likes(self):
        mock_tweets = [{"tweet": {"id_str": "21", "favorite_count": 0}},
                       {"tweet": {"id_str": "22", "favorite_count": 1}},
                       {"tweet": {"id_str": "23", "favorite_count": 2}}]
        mock_args = FakeArguments({"min_likes": 1})

        rows = FakeReader(mock_tweets)
        tweets = TweetReader(rows, mock_args)

        expected = [{"tweet": {"id_str": "21"}}]
        actual = []

        for idx, val in enumerate(tweets.process()):
            self.assertEqual(expected[idx]["tweet"]["id_str"], val["tweet"]["id_str"])
            actual.append(val)

        self.assertEqual(len(expected), len(actual))

    def test_tweet_reader_retweets(self):
        mock_tweets = [{"tweet": {"id_str": "21", "retweet_count": 0}},
                       {"tweet": {"id_str": "22", "retweet_count": 1}},
                       {"tweet": {"id_str": "23", "retweet_count": 2}}]
        mock_args = FakeArguments({"min_retweets": 1})

        rows = FakeReader(mock_tweets)
        tweets = TweetReader(rows, mock_args)

        expected = [{"tweet": {"id_str": "21"}}]
        actual = []

        for idx, val in enumerate(tweets.process()):
            self.assertEqual(expected[idx]["tweet"]["id_str"], val["tweet"]["id_str"])
            actual.append(val)

        self.assertEqual(len(expected), len(actual))

    def test_tweet_reader_min_none_arg(self):
        mock_tweets = [{"tweet": {"id_str": "21", "retweet_count": 0}}]
        mock_args = FakeArguments({"min_likes": None, "min_retweets": None})

        rows = FakeReader(mock_tweets)
        tweets = TweetReader(rows, mock_args)

        expected = [{"tweet": {"id_str": "21"}}]
        actual = []

        for idx, val in enumerate(tweets.process()):
            self.assertEqual(expected[idx]["tweet"]["id_str"], val["tweet"]["id_str"])
            actual.append(val)

        self.assertEqual(len(expected), len(actual))
