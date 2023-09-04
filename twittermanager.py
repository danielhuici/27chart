import tweepy
import yaml
from debug import DEBUG_MODE 

class TwitterManager:
    def __init__(self, logger):
        self.load_credentials()
        self.api = tweepy.Client(bearer_token=self.config['bearer_token'], 
                      access_token=self.config['twitter_access_token'],
                      access_token_secret=self.config['twitter_access_token_secret'],
                      consumer_key=self.config['twitter_consumer_key'],
                      consumer_secret=self.config['twitter_consumer_secret'])
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
        