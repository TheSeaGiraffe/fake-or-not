from pathlib import Path

import pytest

CLEAN_TWEET_GOLDEN_FILE = Path("tests/golden/clean_tweets.txt")
RAW_TWEET_GOLDEN_FILE = Path("tests/golden/raw_tweets.txt")


@pytest.fixture
def load_clean_tweet_golden():
    with open(CLEAN_TWEET_GOLDEN_FILE) as clean:
        return clean.readlines()


@pytest.fixture
def load_raw_tweet_golden():
    with open(RAW_TWEET_GOLDEN_FILE) as raw:
        return raw.readlines()
