from pytube import Playlist, YouTube, exceptions
from yt_dlp import YoutubeDL
import os

from dbmanager import DBManager
from twittermanager import TwitterManager
from gdrivemanager import GDriveManager
from datalayer.song import Song
import logging


SETTINGS_PATH = f"{os.getenv('CREDENTIALS_PATH')}/settings.yaml"
KIFIXO_27_CHART_NAME = "Kifixo 27 Chart"
KIFIXO_TOP_EVER_MUSIC_NAME = "Kifixo TOP-Ever Music"
KIFIXO_GRAND_RESERVA_NAME = "Kifixo Grand Reserva"
SALEN_LISTA_NAME = "Salen de la lista"
SALEN_LISTA_2_NAME = "Salen de la lista 2"
SALEN_LISTA_3_NAME = "Salen de la lista 3"
YOUTUBE_PLAYLIST_URL = "https://www.youtube.com/playlist?list="
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v="
DOWNLOADED_YOUTUBE_SONG_EXTENSION = ".mp3"

class ChartTracker():
    def __init__(self):
        self.dbManager = DBManager()
        self.twitterManager = TwitterManager()
        self.gdriveManager = GDriveManager()
        self.logger = logging.getLogger(__name__)

    def find_playlist_changes(self, db_list, yt_list):
        db_ids = {song.id for song in db_list}
        yt_ids = {song.video_id for song in yt_list}
        
        only_db = [song for song in db_list if song.id not in yt_ids]
        only_yt = [song for song in yt_list if song.video_id not in db_ids]
        
        return only_db, only_yt

    def check_songs_availability(self):
        songs = self.dbManager.get_all_songs()
        for song in songs:
            try:
                YouTube(YOUTUBE_VIDEO_URL + song.id).check_availability()
            except exceptions.VideoUnavailable:
                if self.twitterManager.post_song_status_unavailable_tweet(song):
                    self.dbManager.delete_song(song)

    def download_song(self, song):
        ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(YOUTUBE_VIDEO_URL + song.id)
            
    def backup_songs(self):
        uncommited_songs = self.find_uncommited_songs()
        for song in uncommited_songs:
            self.logger.info(f"Downloading song {song.title}")
            self.download_song(song)
            filename = self.find_song_file()
            self.dbManager.set_filename(song.id, filename)
            self.gdriveManager.upload_file(filename)
            os.remove(filename)

    def database_exists(self):
        for file in os.listdir("."):
            if file == self.dbManager.db_name:
                if os.stat(file).st_size != 0:
                    return True
        return False

    def find_song_file(self):
        for file in os.listdir("."):
            if file.endswith(DOWNLOADED_YOUTUBE_SONG_EXTENSION):
                return file

    def find_uncommited_songs(self):
        db_songs = self.dbManager.get_all_songs()
        gdrive_songs = self.gdriveManager.get_all_file_titles()
        db_songs_aux = db_songs.copy()
        for db_song in db_songs:
            for gdrive_song in gdrive_songs:
                if db_song.filename == gdrive_song:
                    db_songs_aux.remove(db_song)
                    break

        return db_songs_aux 

    def track_playlist_changes(self):
        playlists = self.dbManager.get_playlists()
        for db_playlist in playlists:
            self.logger.info(f"Scanning playlist {db_playlist.title}...")
            current_youtube_playlist = Playlist(f'{YOUTUBE_PLAYLIST_URL}{db_playlist.id}')
            if (len(current_youtube_playlist) > 0): # In case YT returns empty playlist due to error, it won't wipe database
                retired_songs, added_songs = self.find_playlist_changes(db_playlist.songs, current_youtube_playlist.videos)
                self.logger.info(f"Retired songs: {len(retired_songs)} ---- New songs: {len(added_songs)}")

                for song in retired_songs:
                    self.dbManager.deattach_playlist_song(song, db_playlist)
                    if db_playlist.twitter_alert: 
                        self.twitterManager.post_song_status_change_tweet(db_playlist, song, status_added=True)

                for song in added_songs:
                    self.dbManager.insert_video_playlist(Song(song.video_id, song.title, ""), db_playlist)
                    if db_playlist.twitter_alert: 
                        self.twitterManager.post_song_status_change_tweet(db_playlist, song, status_added=False)

    def backup_db(self):
        filename = self.dbManager.generate_sql_backup()
        self.gdriveManager.upload_backup(filename)