import socket
import sys
import requests
import tweepy
import requests_oauthlib
from tweepy.auth import OAuthHandler
import json

# Replace the values below with yours
consumer_key  = "eqLHuY0uTBa0rCfnwUlfheGPc"
consumer_secret = "2BqhyDJwdg2K6DWzcSEX6OKDOExiS5zv2p1inA0lcNDvQT7GzL"
access_token  = "3360443532-TOXKjRYl00GYYSNwAxP6lSwLTfjxBtRTSnTGXqA"
access_token_secret = "yST3YcfLrkqJxjqg3T6JybZiaYGteWGvixIahVjMRb01D"
my_auth = requests_oauthlib.OAuth1(consumer_key, consumer_secret,access_token, access_token_secret)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

conn = None


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        #print(status.text)

        tweet_text = status.text.encode("utf-8")  # pyspark can't accept stream, add '\n'
        print("Tweet Text: ",tweet_text)
        print("------------------------------------------")
        conn.send(tweet_text)



myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)

# def get_tweets():
#     myStream.filter(track = ['#'],locations=[-74.1687, 40.5722, -73.8062, 40.9467])


TCP_IP = "localhost"
TCP_PORT = 9009
conn = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print("Waiting for TCP connection...")
conn, addr = s.accept()
print('conn',conn,'addr',addr)
print("Connected... Starting getting tweets.")
myStream.filter(track = ['#'], languages=["en"], locations=[-74.1687, 40.5722, -73.8062, 40.9467])



