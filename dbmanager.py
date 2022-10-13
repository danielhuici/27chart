import logging
import sqlite3

from playlist import Playlist
from song import Song

DB_NAME = "27chart.db"
SQL_TABLE_PLAYLIST = """CREATE TABLE playlists (
         "id"            TEXT PRIMARY KEY NOT NULL,
         "title"         TEXT NOT NULL,
         "twitter_alert" INTEGER NOT NULL);
"""

SQL_TABLE_MUSIC = """CREATE TABLE songs (
         "id"            TEXT PRIMARY KEY NOT NULL,
         "title"         TEXT NOT NULL,
         "filename"      TEXT);
"""

SQL_TABLE_PLAYLIST_SONG = """CREATE TABLE "playlist_song" (
          "id"           INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          "playlist_id"  INT REFERENCES playlists(id),
          "song_id"      INT REFERENCES songs(id));
"""

SQL_GET_PLAYLISTS = "SELECT * FROM playlists"
SQL_GET_ALL_SONGS = "SELECT * FROM songs"
SQL_GET_MUSIC_PLAYLIST = "SELECT * FROM songs WHERE id IN (SELECT song_id FROM playlist_song WHERE playlist_id = ?)"
SQL_INSERT_PLAYLIST = "INSERT INTO playlists (id, title) VALUES (?, ?)"
SQL_INSERT_MUSIC = "INSERT INTO songs (id, title) VALUES (?, ?)"
SQL_ATTACH_SONG_PLAYLIST = "INSERT INTO playlist_song (playlist_id, song_id) VALUES (?, ?)"
SQL_DEATTACH_SONG_PLAYLIST = "DELETE FROM playlist_song WHERE playlist_id = ? and song_id = ?"
SQL_DEATTACH_SONG_ALL_PLAYLIST = "DELETE FROM playlist_song WHERE song_id = ?"
SQL_SET_SONG_FILENAME = "UPDATE songs SET filename = ? WHERE id = ?"
SQL_DELETE_SONG =  "DELETE FROM songs WHERE song_id = ?"

class DBManager():
    def __init__(self):
        self.db_name = DB_NAME
        self.connection = sqlite3.connect(DB_NAME)
        logging.debug("Opened database successfully")

    def create_tables(self):
        self.connection.cursor().execute(SQL_TABLE_MUSIC)
        self.connection.cursor().execute(SQL_TABLE_PLAYLIST)
        self.connection.cursor().execute(SQL_TABLE_PLAYLIST_SONG)
        self.insert_playlist("PLaJq2Gw03Eii0OIzVxV62AISH1A9xOfWw", "Kifixo 27 Chart", 1)
        self.insert_playlist("PLaJq2Gw03EijUkrVadSIA9Gxll7ewZ4oY", "Kifixo TOP-Ever Music", 1)
        self.insert_playlist("PLaJq2Gw03EiiuyuyumGeqYeR6FBz3jRyG", "Kifixo Grand Reserva", 1)
        self.insert_playlist("PLaJq2Gw03Eig3nRIkMQpi2XgfEoJe6S0G", "Salen de la lista", 0)
        self.insert_playlist("PLaJq2Gw03Eigv6RQqXKmUP8lPO3IoXbEl", "Salen de la lista 2", 0)

    def get_playlists(self):
        cursor = self.connection.cursor().execute(SQL_GET_PLAYLISTS)
        playlists = []
        for row in cursor.fetchall():
            print(row)
            p = Playlist(*row)
            p.songs = self.get_music_playlist(p.id)
            playlists.append(p)

        return playlists

    def get_music_playlist(self, playlist_id):
        cursor = self.connection.cursor().execute(SQL_GET_MUSIC_PLAYLIST, (playlist_id,))
        rows = cursor.fetchall()
        songs = []
        for row in rows:
            songs.append(Song(*row))

        return songs

    def get_all_songs(self):
        cursor = self.connection.cursor().execute(SQL_GET_ALL_SONGS)
        rows = cursor.fetchall()
        songs = []
        for row in rows:
            songs.append(Song(*row))

        return songs

    def insert_playlist(self, id, title, twitter_alert):
        cursor = self.connection.cursor().execute(SQL_INSERT_PLAYLIST, (id, title, twitter_alert))
        self.connection.commit()
        cursor.close()

    def insert_song(self, song): 
        tuple = (song.id, song.title)
        cursor = self.connection.cursor().execute(SQL_INSERT_MUSIC, tuple)
        self.connection.commit()
        cursor.close()    

    # Will insert the song. If it already exists on the DB, it will just attach the song to the playlist.
    def insert_video_playlist(self, song, playlist): 
        try: 
            self.insert_song(song)
        except sqlite3.IntegrityError:
            pass

        tuple = (playlist.id, song.id)
        cursor = self.connection.cursor().execute(SQL_ATTACH_SONG_PLAYLIST, tuple)
        self.connection.commit()
        cursor.close()

    def deattach_playlist_song(self, song, playlist):
        tuple = (playlist.id, song.id)
        cursor = self.connection.cursor().execute(SQL_DEATTACH_SONG_PLAYLIST, tuple)
        self.connection.commit()
        cursor.close()

    def delete_song(self, song):
        cursor = self.connection.cursor().execute(SQL_DEATTACH_SONG_ALL_PLAYLIST, (song.id,) )
        self.connection.commit()
        cursor = self.connection.cursor().execute(SQL_DELETE_SONG, (song.id,))
        self.connection.commit()
        cursor.close()


    def set_filename(self, song_id, filename):
        cursor = self.connection.cursor().execute(SQL_SET_SONG_FILENAME, (filename, song_id))
        self.connection.commit()
        cursor.close()