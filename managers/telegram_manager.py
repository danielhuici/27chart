import os
import logging
import requests
from typing import Optional
from dotenv import load_dotenv

from datalayer.song import Song
from common.utils import debug_mode

TELEGRAM_TEMPLATES = {
    "Kifixo 27 Chart": {
        "added": "✅ ENTRADA EN LISTA #Kifixo27Chart \n {} \n youtu.be/{}",
        "retired": "❌ SALE DE LA LISTA #Kifixo27Chart \n {} \n youtu.be/{}"
    },
    "Kifixo TOP-Ever Music": {
        "added": "🔝 ✅ ENTRADA EN #KifixoTopEverMusic \n {} \n youtu.be/{}",
        "retired": "🔝 ❌ SALIDA DE #KifixoTopEverMusic \n {} \n youtu.be/{}"
    },
    "Kifixo Grand Reserva": {
        "added": "⭐ Congratulations ⭐ \n ENTRADA A #KifixoGrandReserva Y CANDIDATA A #KifixoSong2026 \n {} \n youtu.be/{}",
        "retired": "🟡 THANK YOU 🟡 \n Salida #KifixoGrandReserva y revelada para Kifixo 27 Chart \n {} \n youtu.be/{}"
    },
    "Song Unavailable": "❗ Una canción ya no está disponible #NoDisponible❗ \n Lista: {} \n Canción: {} \n youtu.be/{}\n"
}

class TelegramManager:
    """Manages Telegram interactions for posting song-related messages."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        if not os.getenv('TELEGRAM_BOT_TOKEN'):
            load_dotenv()

        self._validate_telegram_credentials()
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.logger = logger or logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _validate_telegram_credentials(self) -> None:
        required_credentials = [
            'TELEGRAM_BOT_TOKEN', 
            'TELEGRAM_CHAT_ID'
        ]
        
        missing_credentials = [
            cred for cred in required_credentials 
            if not os.getenv(cred)
        ]
        
        if missing_credentials:
            raise ValueError(f"Missing Telegram credentials: {', '.join(missing_credentials)}")

    def _post(self, text: str) -> bool:
        if debug_mode():
            self.logger.info(f"[DEBUG] Would send Telegram message: {text}")
            return True

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return True

        except Exception as e:
            self.logger.error(f"Telegram message sending failed: {text}\nError: {e}")
            return False

    def post_song_status_change(self, playlist_title: str, song: Song, status_added: bool) -> bool:
        try:
            text = self._create_message_text(playlist_title, song, status_added)
            self.logger.info(f"Sending song status change message: {text}")
            return self._post(text)
        except KeyError as e:
            self.logger.error(f"Invalid playlist or message template: {e}")
            return False

    def post_song_unavailable(self, playlist: str, song: Song) -> bool:
        try:
            template = TELEGRAM_TEMPLATES.get("Song Unavailable", "")
            text = template.format(playlist, song.title, song.id)
            self.logger.info(f"Sending song unavailable message: {text}")
            return self._post(text)
        except Exception as e:
            self.logger.error(f"Failed to send unavailable song message: {e}")
            return False

    def _create_message_text(self, playlist_title: str, song: Song, status_added: bool) -> str:
        templates = TELEGRAM_TEMPLATES.get(playlist_title, {})
        if status_added:
            return templates.get("added", "").format(song.title, song.id)
        return templates.get("retired", "").format(song.title, song.id)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    manager = TelegramManager()
    manager._post("Test message from Kifixo Telegram Manager")
