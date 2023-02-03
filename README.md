# delete-tweets

This is a simple script that enables you to delete tweets from your timeline. There are  third-party services that allow you to delete tweets, but they will not allow you to delete tweets beyond the infamous [3,200 tweet limit](https://web.archive.org/web/20131019125213/https://dev.twitter.com/discussions/276).

_Credit to [@koenrh](koenrh/delete-tweets) for the original project._

## Prerequisites

**Note:** As of late 2018, you are required to have a Twitter Developer account in order to create a Twitter app.

### Apply for a Twitter Developer account

1. [Create a Twitter Developer account](https://developer.twitter.com/en/apply): You will need to provide details of your use case:
   1. **User profile**: Use your current Twitter @username.
   1. **Account details**: Select *I am requesting access for my own personal use*, set your 'Account name' to your @username, and select your 'Primary country of operation.
   1. **Use case details**: select 'Other', and explain in at least 300 words that
   you want to create an app to semi-automatically clean up your own tweets.
   1. **Terms of service**: Read and accept the terms.
   1. **Email verification**: Confirm your email address.
1. Now wait for your Twitter Developer account to be reviewed and approved.

### Create a Twitter app

1. [Create a new Twitter app](https://developer.twitter.com/en/apps/create) (not
  available as long as your Twitter Developer account is pending review).
1. Set 'Access permissions' of your app to *Read and write*.

### Configure your environment

1. Open your Twitter Developer's [apps](https://developer.twitter.com/en/apps).
1. Click the 'Details' button next to your newly created app.
1. Click the 'Keys and tokens' tab, and find your keys, secret keys and access tokens.
1. Now you need to make these keys and tokens available to your shell environment.


### Setup your credentials

1. Create a new `.env` file in the root of the project
2. Use the `.env-template` as a guide.
3. Replace the key, secrets and token with the values from Twitter.


### Get your tweet archive

1. Open the [Your Twitter data page](https://twitter.com/settings/your_twitter_data)
1. Scroll to the 'Download your Twitter data' section at the bottom of the page
1. Re-enter your password
1. Click 'Request data', and wait for the email to arrive
1. Follow the link in the email to download your Tweet data
1. Unpack the archive

## Getting started

### Pre-requisites

You will need the following:

1. `pyenv` to install the correct version of Python.
1. `virtualenv` to create isolated Python environment.

### Setup local development

Install the required version of Python and setup a new virtual environment.
```bash
$ pyenv install
$ virtualenv .venv --prompt=delete-tweets
$ source .venv/bin/activate
(delete-tweets) $
```

Once you're in your isolated Python environment, you can upgrade and install dependencies.

```bash
pip install --upgrade pip
pip install -r requirements-dev.txt
```
You can then run the linter and unit tests:
```bash
flake8
pytest
```

### Usage

Delete any tweet from _before_ January 1, 2018:

```bash
delete-tweets --until 2018-01-01 tweet.js
```

Or only delete all retweets:

```bash
delete-tweets --filter retweets tweet.js
```

### Spare tweets

You can optionally spare tweets by passing their `id_str`, setting a minimum
amount of likes or retweets:

```bash
delete-tweets --until 2018-01-01 tweet.js --spare-ids 21235434 23498723 23498723
```

Spare tweets that have at least 10 likes, or 5 retweets:

```bash
delete-tweets --until 2018-01-01 tweet.js --spare-min-likes 10 --spare-min-retweets 5
```
