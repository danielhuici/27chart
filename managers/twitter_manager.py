import tweepy
import os
import logging
from debug import DEBUG_MODE
from datalayer.song import Song

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
        "added": "\U00002B50 Congratulations \U00002B50 \n ENTRADA A #KifixoGrandReserva Y CANDIDATA A #KifixoSong2024 \n {} \n youtu.be/{}",
        "retired": "\U0001F7E1 THANK YOU \U0001F7E1 \n Salida #KifixoGrandReserva y revelada para Kifixo 27 Chart \n {} \n youtu.be/{}"
    },
    "Song Unavailable": "\U00002757 Una canción ya no está disponible @kifixo23 \U00002757 \n {} youtu.be/{}\n"
}

class TwitterManager:
    def __init__(self):
        self.api = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRECT'),
            consumer_key=os.getenv('TWITTER_CONSUMER_KEY'),
            consumer_secret=os.getenv('TWITTER_CONSUMER_KEY_SECRET')
        )

        self.logger = logging.getLogger(__name__)

    def _post(self, text: str):
        if not DEBUG_MODE:
            try:
                return True
                self.api.create_tweet(text=text)
            except Exception as e:
                self.logger.error(f"Couldn't post tweet: {text}\n{e}")
                return False
        return False

    def post_song_status_change_tweet(self, playlist_title: str, song: Song, status_added: bool):
        added_song_tweet, retired_song_tweet = self.build_tweet(playlist_title, song)
        text = added_song_tweet if status_added else retired_song_tweet

        self.logger.info(f"POST TWEET - Song status changed: {text}")
        return self._post(text)

    def post_song_status_unavailable_tweet(self, song: Song):
        tweet_template = TWEET_TEMPLATES.get("Song Unavailable", "")
        text = tweet_template.format(song.title, song.id)

        self.logger.info(f"POST TWEET - Song became unavailable: {text}")
        return self._post(text)

    def build_tweet(self, playlist_title: str, song: Song):
        tweets_templates = TWEET_TEMPLATES.get(playlist_title, {})
        added_song_tweet = tweets_templates.get("added", "").format(song.title, song.id)
        retired_song_tweet = tweets_templates.get("retired", "").format(song.title, song.id)

        return added_song_tweet, retired_song_tweet

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    manager = TwitterManager()
    manager.post_song_status_change_tweet("Test")