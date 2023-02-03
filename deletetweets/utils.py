from dateutil import parser


def parse_date(dt):
    return parser.parse(dt, ignoretz=True)


def log(tweet_id, message):
    print('[%s] %s' % (tweet_id, message))
