import os
import logging
from typing import Optional, Tuple, Dict
import tweepy
from dotenv import load_dotenv

from datalayer.song import Song
from common.utils import debug_mode

TWEET_TEMPLATES = {
    "Kifixo 27 Chart": {
        "added": "\U00002705 ENTRADA EN LISTA #Kifixo27Chart \n {} \n youtu.be/{}",
        "retired": "\U0000274C SALE DE LA LISTA #Kifixo27Chart \n {} \n youtu.be/{}"
    },
    "Kifixo TOP-Ever Music": {
        "added": "\U0001F51D \U00002705 ENTRADA EN #KifixoTopEverMusic \n {} \n youtu.be/{}",
        "retired": "\U0001F51D \U0000274C SALIDA DE #KifixoTopEverMusic \n {} \n youtu.be/{}"
    },
    "Kifixo Grand Reserva": {
        "added": "\U00002B50 Congratulations \U00002B50 \n ENTRADA A #KifixoGrandReserva Y CANDIDATA A #KifixoSong2026 \n {} \n youtu.be/{}",
        "retired": "\U0001F7E1 THANK YOU \U0001F7E1 \n Salida #KifixoGrandReserva y revelada para Kifixo 27 Chart \n {} \n youtu.be/{}"
    },
    "Song Unavailable": "\U00002757 Una canción ya no está disponible @kifixo23 \U00002757 \n Lista: {} \n Canción: {} \n youtu.be/{}\n"
}

class TwitterManager:
    """Manages Twitter interactions for posting song-related tweets."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        if not os.getenv('TWITTER_BEARER_TOKEN'):
            load_dotenv()

        self._validate_twitter_credentials()

        try:
            self.api = tweepy.Client(
                bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),  # Fixed typo
                consumer_key=os.getenv('TWITTER_CONSUMER_KEY'),
                consumer_secret=os.getenv('TWITTER_CONSUMER_KEY_SECRET')
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Twitter API: {e}")

        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _validate_twitter_credentials(self) -> None:
        required_credentials = [
            'TWITTER_BEARER_TOKEN', 
            'TWITTER_ACCESS_TOKEN', 
            'TWITTER_ACCESS_TOKEN_SECRET', 
            'TWITTER_CONSUMER_KEY', 
            'TWITTER_CONSUMER_KEY_SECRET'
        ]
        
        missing_credentials = [
            cred for cred in required_credentials 
            if not os.getenv(cred)
        ]
        
        if missing_credentials:
            raise ValueError(f"Missing Twitter credentials: {', '.join(missing_credentials)}")

    def _post(self, text: str) -> bool:
        if debug_mode():
            self.logger.info(f"[DEBUG] Would post tweet: {text}")
            return True

        try:
            self.api.create_tweet(text=text)
            self.logger.info(f"Tweet posted successfully!")
            return True
        except Exception as e:
            self.logger.error(f"Tweet posting failed: {text}\nError: {e}")
            return False

    def post_song_status_change_tweet(self, playlist_title: str, song: Song, status_added: bool) -> bool:
        try:
            text = self._create_tweet_text(playlist_title, song, status_added)
            self.logger.info(f"Posting song status change tweet: {text}")
            return self._post(text)
        except KeyError as e:
            self.logger.error(f"Invalid playlist or tweet template: {e}")
            return False

    def post_song_unavailable_tweet(self, playlist: str, song: Song) -> bool:
        try:
            text = TWEET_TEMPLATES.get("Song Unavailable", "").format(playlist, song.title, song.id)
            self.logger.info(f"Posting song unavailable tweet: {text}")
            return self._post(text)
        except Exception as e:
            self.logger.error(f"Failed to post unavailable song tweet: {e}")
            return False

    def _create_tweet_text(self, playlist_title: str, song: Song, status_added: bool) -> str:
        tweets_templates = TWEET_TEMPLATES.get(playlist_title, {})
        added_song_tweet = tweets_templates.get("added", "").format(song.title, song.id)
        retired_song_tweet = tweets_templates.get("retired", "").format(song.title, song.id)

        return added_song_tweet, retired_song_tweet

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    manager = TwitterManager()
    manager.post_song_status_change_tweet("Test")
