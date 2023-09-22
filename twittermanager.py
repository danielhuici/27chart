import tweepy
import yaml
import os
from debug import DEBUG_MODE 

class TwitterManager:
    def __init__(self, logger):
        self.api = tweepy.Client(bearer_token=os.getenv("BEARER_TOKEN"), 
                      access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                      access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRECT"),
                      consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
                      consumer_secret=os.getenv("TWITTER_CONSUMER_KEY_SECRET"))
        self.logger = logger


    def load_credentials(self):
        with open('settings.yaml', 'r') as file:
            self.config = yaml.safe_load(file)

    def post_tweet(self, text):
        if DEBUG_MODE:
            self.logger.info(f"[TwitterManager] Sending tweet: {text}")
        else:
            try:
                self.logger.info(f"[TwitterManager] Sending tweet: {text}")
                self.api.create_tweet(text=text)
            except Exception as e:
                self.logger.info(f"[TwitterManager] Couldn't send tweet: {text} \n {e}")
        