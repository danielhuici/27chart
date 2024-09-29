import psycopg2
import subprocess
import os
from datalayer.playlist import Playlist
from datalayer.song import Song
from datetime import date
from common.utils import debug_mode
import logging

SQL_GET_PLAYLISTS = "SELECT * FROM playlists"
SQL_GET_SONG = "SELECT * FROM songs WHERE id = %s"
SQL_GET_ALL_SONGS = "SELECT * FROM songs"
SQL_CHECK_SONG_EXISTS = "SELECT id FROM songs WHERE id = %s"
SQL_GET_SONGS_PLAYLIST = "SELECT * FROM songs WHERE id IN (SELECT song_id FROM playlist_song WHERE playlist_id = %s)"
SQL_CHECK_SONG_IS_ATTACHED = "SELECT * FROM playlist_song WHERE song_id = %s"
SQL_INSERT_PLAYLIST = "INSERT INTO playlists (id, title) VALUES (%s, %s)"
SQL_INSERT_MUSIC = "INSERT INTO songs (id, title) VALUES (%s, %s)"
SQL_ATTACH_SONG_PLAYLIST = "INSERT INTO playlist_song (playlist_id, song_id) VALUES (%s, %s)"
SQL_DEATTACH_SONG_PLAYLIST = "DELETE FROM playlist_song WHERE playlist_id = %s and song_id = %s"
SQL_DEATTACH_SONG_ALL_PLAYLIST = "DELETE FROM playlist_song WHERE song_id = %s"
SQL_SET_SONG_FILENAME = "UPDATE songs SET filename = %s WHERE id = %s"
SQL_SET_SONG_TITLE = "UPDATE songs SET title = %s WHERE id = %s"
SQL_DELETE_SONG =  "DELETE FROM songs WHERE id = %s"

class DBManager():
    def __init__(self):
        self.connection = psycopg2.connect(
                        database = os.getenv('DB_NAME'),
                        host = os.getenv('DB_HOST'),
                        user = os.getenv('DB_USER'),
                        password = os.getenv('PGPASSWORD'),
                        port = os.getenv('DB_PORT'))
        self.cursor = self.connection.cursor()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Database connection successful")

    def get_playlists(self):
        self.cursor.execute(SQL_GET_PLAYLISTS)

        playlists = []
        for row in self.cursor.fetchall():
            p = Playlist(*row)
            p.songs = self.get_songs_playlist(p.id)
            playlists.append(p)

        return playlists

    def get_songs_playlist(self, playlist_id):
        self.cursor.execute(SQL_GET_SONGS_PLAYLIST, (playlist_id,))
        rows = self.cursor.fetchall()
        songs = []
        for row in rows:
            songs.append(Song(*row))

        return songs
    
    def get_song(self, song_id):
        self.cursor.execute(SQL_GET_SONG, (song_id, ))
        row = self.cursor.fetchone()
        if row:
            return Song(*row)
        return None
        
    def get_all_songs(self):
        self.cursor.execute(SQL_GET_ALL_SONGS)
        rows = self.cursor.fetchall()
        songs = []
        for row in rows:
            songs.append(Song(*row))

        return songs

    def song_exists(self, song):
        self.cursor.execute(SQL_CHECK_SONG_EXISTS, (song.id,))
        return self.cursor.fetchone() is not None

    def insert_playlist(self, id, title, twitter_alert):
        self.cursor.execute(SQL_INSERT_PLAYLIST, (id, title, twitter_alert))
        self.connection.commit()
        
    def insert_song(self, song): 
        tuple = (song.id, song.title)
        self.cursor.execute(SQL_INSERT_MUSIC, tuple),
        self.connection.commit()

    # Will insert the song. If it already exists on the DB, it will just attach the song to the playlist.
    def insert_video_playlist(self, song, playlist): 
        if not self.song_exists(song): 
            self.insert_song(song)

        self.cursor.execute(SQL_ATTACH_SONG_PLAYLIST, (playlist.id, song.id))
        self.connection.commit()

    def is_song_attached_to_some_playlist(self, song):
        self.cursor.execute(SQL_CHECK_SONG_IS_ATTACHED, (song.id,))
        return self.cursor.fetchone() is not None

    def deattach_playlist_song(self, song, playlist):
        self.cursor.execute(SQL_DEATTACH_SONG_PLAYLIST, (playlist.id, song.id))
        self.connection.commit()

    def delete_song(self, song):
        self.cursor.execute(SQL_DEATTACH_SONG_ALL_PLAYLIST, (song.id,))
        self.cursor.execute(SQL_DELETE_SONG, (song.id,))
        self.connection.commit()

    def set_filename(self, song_id, filename):
        self.cursor.execute(SQL_SET_SONG_FILENAME, (filename, song_id))
        self.connection.commit()

    def set_song_title(self, song_id, title):
        self.cursor.execute(SQL_SET_SONG_TITLE, (title, song_id))
        self.connection.commit()

    def generate_sql_backup(self):
        filename = f"27chart{date.today()}.sql"
        command = ["pg_dump", "-h", os.getenv('DB_HOST'), "-p", os.getenv('DB_PORT'),
                   "-Fc", "-b", "-U", os.getenv('DB_USER'), "-d", os.getenv('DB_NAME'),
                   "-f", filename]
        
        subprocess.run(command)   
         
        return filename

