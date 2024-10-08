import os
from managers.db_manager import DBManager
from managers.twitter_manager import TwitterManager
from managers.google_drive_manager import GoogleDriveManager
from managers.youtube_scrapper import YoutubeScrapper
from managers.youtube_downloader import YoutubeDownloader

import logging

SETTINGS_PATH = f"{os.getenv('CREDENTIALS_PATH')}/settings.yaml"
YOUTUBE_PLAYLIST_BASEURL = "https://www.youtube.com/playlist?list="
SONG_FILE_EXTENSION = ".mp3"

YT_DLP_OPTS = {'username': 'oauth2',
            'password': '',
            'quiet': True,
            'no_warnings': True}

class ChartTracker():
    def __init__(self, db_manager : DBManager, gdrive_manager: GoogleDriveManager):
        self.db_manager = db_manager
        self.twitterManager = TwitterManager()
        self.gdrive_manager = gdrive_manager
        self.youtube_scrapper = YoutubeScrapper()
        self.youtube_downloader = YoutubeDownloader()
        self.logger = logging.getLogger(__name__)

    def find_playlist_changes(self, db_songs, youtube_songs):
        unpresents_youtube_songs = set(db_songs).difference(youtube_songs)
        added_youtube_songs = set(youtube_songs).difference(db_songs)

        unavailable_songs = []
        removed_youtube_songs = []
        for song in unpresents_youtube_songs:
            self.logger.info(f"Deleted song {song} from playlist.")
            if self.youtube_downloader.check_video_availability(song):
                removed_youtube_songs.append(song)
            else:
                unavailable_songs.append(song)

        return added_youtube_songs, removed_youtube_songs, unavailable_songs

    def handle_unavailable_songs(self, unavailable_songs):
        for song in unavailable_songs:
            if self.twitterManager.post_song_status_unavailable_tweet(song):
                self.db_manager.delete_song(song)

    def backup_songs(self):
        unsaved_songs = self._find_unsaved_songs()
        for song in unsaved_songs:
            song_filename = self.gdrive_manager.is_file_present(song.id)
            if not song_filename: # Song is not in Google Drive, download it then!
                self.logger.info(f"Downloading song {song.title}")
                self.youtube_downloader.download_song(song)
                song_filename = self._find_song_file()
                self.gdrive_manager.upload_file(song_filename)
                os.remove(song_filename)
            self.db_manager.set_song_filename(song.id, song_filename)
            
    def _find_song_file(self):
        for file in os.listdir("."):
            if file.endswith(SONG_FILE_EXTENSION):
                return file

    def _find_unsaved_songs(self):
        db_songs = self.db_manager.get_all_songs()
        unsaved_songs = []
        for song in db_songs:
            if song.filename == None:
                unsaved_songs.append(song)

        return unsaved_songs 

    def handle_playlist_changes(self, playlist, retired_songs, added_songs, twitter_alert=False):
        for song in added_songs:
            self.db_manager.insert_video_playlist(song, playlist)
            if twitter_alert: 
                self.twitterManager.post_song_status_change_tweet(playlist.title, song, status_added=True)

        for song in retired_songs: 
            self.db_manager.deattach_playlist_song(song, playlist)
            if twitter_alert: 
                self.twitterManager.post_song_status_change_tweet(playlist.title, song, status_added=False)

    def clean_dettached_songs(self):
        dettached_songs = self.db_manager.get_dettached_songs()
        for song in dettached_songs:
            self.db_manager.delete_song(song)

    def track_playlist_changes(self):
        playlists = self.db_manager.get_playlists()
        for db_playlist in playlists:
            current_db_playlist_songs = self.db_manager.get_songs_playlist(db_playlist.id)
            success, current_youtube_playlist_songs = self.youtube_scrapper.get_available_playlist_videos(db_playlist.id)
            if success:
                added_songs, retired_songs, unavailable_songs = self.find_playlist_changes(current_db_playlist_songs, current_youtube_playlist_songs)
                self.handle_unavailable_songs(unavailable_songs)
                self.logger.info(f"[{db_playlist.title}] Retired songs: {len(retired_songs)} | New songs: {len(added_songs)} | Unavailable songs: {len(unavailable_songs)}")
                self.handle_playlist_changes(db_playlist, retired_songs, added_songs, db_playlist.twitter_alert)
            else:
                self.logger.warning(f"Something worng happend while scrapping YouTube playlist ({db_playlist}). We'll try again later...")
        self.clean_dettached_songs()

    def backup_db(self):
        filename = self.db_manager.generate_sql_backup()
        self.gdrive_manager.upload_backup(filename)
        os.remove(filename)
