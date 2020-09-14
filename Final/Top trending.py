import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
import collections
from send_mongo import monsendmany

import tweepy as tw
import nltk
from nltk.corpus import stopwords
import re
import networkx

import warnings
import pymongo


# 3.md: regular expressions #
def remove_url(txt):
    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())


def main():
    warnings.filterwarnings("ignore")

    sns.set(font_scale=1.5)
    sns.set_style("whitegrid")

    # 1.md: authentication #

    # input your credentials here
    consumer_key = "eqLHuY0uTBa0rCfnwUlfheGPc"
    consumer_secret = "2BqhyDJwdg2K6DWzcSEX6OKDOExiS5zv2p1inA0lcNDvQT7GzL"
    access_token = "3360443532-TOXKjRYl00GYYSNwAxP6lSwLTfjxBtRTSnTGXqA"
    access_token_secret = "yST3YcfLrkqJxjqg3T6JybZiaYGteWGvixIahVjMRb01D"

    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)

    # 2.md: searching #
    search_term = "#COVID19"

    tweets = tw.Cursor(api.search,
                       q=search_term,
                       lang="en",
                       since='2020-5-7').items(1000)

    all_tweets = [tweet.text for tweet in tweets]

    print(all_tweets[:5])
    all_tweets_no_urls = [remove_url(tweet) for tweet in all_tweets]
    print(all_tweets_no_urls[:5])

    # 4.md - Generating list of most common words into DataFrame #

    # Split the words from one tweet into unique elements
    print(all_tweets_no_urls[0].split())

    # Split the words from one tweet into unique elements
    print(all_tweets_no_urls[0].lower().split())

    # Create a list of lists containing lowercase words for each tweet
    words_in_tweet = [tweet.lower().split() for tweet in all_tweets_no_urls]
    print(words_in_tweet[:2])

    # List of all words across tweets
    stop_words = set(stopwords.words('english'))
    all_words_no_urls = list(itertools.chain(*words_in_tweet))
    filtered_sentence = []

    for w in all_words_no_urls:
        if w not in stop_words:
            filtered_sentence.append(w)
    # Create counter
    counts_no_urls = collections.Counter(filtered_sentence)

    print(counts_no_urls.most_common(15))

    clean_tweets_no_urls = pd.DataFrame(counts_no_urls.most_common(30),
                                        columns=['content', 'content_count'])

    print(clean_tweets_no_urls.head())
    monsendmany(clean_tweets_no_urls, "Newyork_tophash")
    # 5.md - plotting horizontal bar graph #

    fig, ax = plt.subplots(figsize=(8,8))
    # Plot horizontal bar graph
    clean_tweets_no_urls.sort_values(by='count').plot.barh(x='words',
                                                           y='count',
                                                           ax=ax,
                                                           color="purple")

    ax.set_title("Common Words Found in Tweets")

    plt.show()


main()