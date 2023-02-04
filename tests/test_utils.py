import pytest

from unittest import TestCase
from deletetweets import utils


class TestUtils(TestCase):
    def test_parse_date_removes_tz(self):
        mock_date = "Sat Jan 08 19:46:36 +0000 2022"
        expected = "2022-01-08 19:46:36"
        actual = str(utils.parse_date(mock_date))
        self.assertEqual(expected, actual)

    @pytest.fixture(autouse=True)
    def capfd(self, capfd):
        self.capfd = capfd

    def test_log_format(self):
        mock_tweet_id = "1"
        mock_message = "foobar"
        expected = "[%s] %s\n" % (mock_tweet_id, mock_message)

        utils.log(mock_tweet_id, mock_message)

        actual, err = self.capfd.readouterr()
        self.assertEqual(expected, actual)
