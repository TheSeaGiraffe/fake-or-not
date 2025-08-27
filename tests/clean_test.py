from app.services.data_clean import clean_all_texts


def test_clean_all_texts(load_raw_tweet_golden, load_clean_tweet_golden):
    got = clean_all_texts(load_raw_tweet_golden)
    assert got == load_clean_tweet_golden
