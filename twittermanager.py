import tweepy
import yaml
from debug import DEBUG_MODE 

class TwitterManager:
    def __init__(self, logger):
        self.load_credentials()
        self.auth = tweepy.OAuthHandler(self.config['twitter_api_key'], self.config['twitter_secret'])
        self.auth.set_access_token(self.config['twitter_access_token'], self.config['twitter_access_token_secret'])
        self.api = tweepy.API(self.auth)
        self.logger = logger


    def load_credentials(self):
        with open('settings.yaml', 'r') as file:
            self.config = yaml.safe_load(file)

    def postTweet(self, text):
        if DEBUG_MODE:
            self.logger.info(f"[TwitterManager] Sending tweet: {text}")
        else:
            try:
                self.logger.info(f"[TwitterManager] Sending tweet: {text}")
                self.api.update_status(text)
            except Exception as e:
                self.logger.info(f"[TwitterManager] Couldn't send tweet: {text} \n {e}")
        