from __future__ import unicode_literals
import logging
import os
from time import sleep
from pytube import Playlist, YouTube, exceptions
from yt_dlp import YoutubeDL
from dbmanager import DBManager
from twittermanager import TwitterManager
from gdrivemanager import GDriveManager
from song import Song

ONE_HOUR = 3600
KIFIXO_27_CHART_NAME = "Kifixo 27 Chart"
KIFIXO_TOP_EVER_MUSIC_NAME = "Kifixo TOP-Ever Music"
KIFIXO_GRAND_RESERVA_NAME = "Kifixo Grand Reserva"
SALEN_LISTA_NAME = "Salen de la lista"
SALEN_LISTA_2_NAME = "Salen de la lista 2"
SALEN_LISTA_3_NAME = "Salen de la lista 3"
KIFIXO_27_CHART_DELETED_SONG_TWEET = "\U0000274C SALE DE LA LISTA #Kifixo27Chart \n {} \n youtu.be/{}"
KIFIXO_27_CHART_NEW_SONG_TWEET = "\U00002705 ENTRADA EN LISTA #Kifixo27Chart \n {} \n youtu.be/{}"
KIFIXO_TOP_EVER_DELETED_SONG_TWEET = "\U0001F51D \U0000274C SALIDA DE #KifixoTopEverMusic \n {} \n youtu.be/{}"
KIFIXO_TOP_EVER_NEW_SONG_TWEET = "\U0001F51D \U00002705 ENTRADA EN #KifixoTopEverMusic \n {} \n youtu.be/{}"
KIFIXO_GRAND_RESERVA_DELETED_SONG_TWEET = "\U0001F7E1 THANK YOU \U0001F7E1 \n Salida #KifixoGrandReserva y revelada para Kifixo 27 Chart \n {} \n youtu.be/{}"
KIFIXO_GRAND_RESERVA_NEW_SONG_TWEET = "\U00002B50 Congratulations \U00002B50 \n ENTRADA A #KifixoGrandReserva Y CANDIDATA A #KifixoSong2023 \n {} \n youtu.be/{}"
SONG_BECAME_UNAVAILABLE_TWEET = "\U00002757 Una canción ya no está disponible @kifixo23 \U00002757 \n {} youtu.be/{}\n"
YOUTUBE_PLAYLIST_URL = "https://www.youtube.com/playlist?list="
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v="
FILE_EXTENSION = ".mp3"


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
dbManager = DBManager()
twitterManager = TwitterManager(logger)
gdriveManager = GDriveManager()

def find_playlist_changes(db_list, yt_list):
    yt_list = list(yt_list)
    db_list_aux = db_list.copy()
    yt_list_aux = yt_list.copy()
    for db_song in db_list:
        for yt_song in yt_list:
            if db_song.id == yt_song.video_id:
                db_list_aux.remove(db_song)
                yt_list_aux.remove(yt_song)
                
    return db_list_aux, yt_list_aux

def handle_lists(db_playlist):
    added_song_tweet = ""
    retired_song_tweet = ""
    if db_playlist.title == KIFIXO_27_CHART_NAME:
        added_song_tweet = KIFIXO_27_CHART_NEW_SONG_TWEET
        retired_song_tweet = KIFIXO_27_CHART_DELETED_SONG_TWEET
    elif db_playlist.title == KIFIXO_TOP_EVER_MUSIC_NAME:
        added_song_tweet = KIFIXO_TOP_EVER_NEW_SONG_TWEET
        retired_song_tweet = KIFIXO_TOP_EVER_DELETED_SONG_TWEET
    elif db_playlist.title == KIFIXO_GRAND_RESERVA_NAME:
        added_song_tweet = KIFIXO_GRAND_RESERVA_NEW_SONG_TWEET
        retired_song_tweet = KIFIXO_GRAND_RESERVA_DELETED_SONG_TWEET

    p = Playlist(f'{YOUTUBE_PLAYLIST_URL}{db_playlist.id}')
    retired_songs, added_songs = find_playlist_changes(db_playlist.songs, p.videos)
    logger.info("Retired songs: " + str(len(retired_songs)) + " New songs: " + str(len(added_songs)))

    for song in retired_songs:
        dbManager.deattach_playlist_song(song, db_playlist)
        if db_playlist.twitter_alert: 
            tweet = retired_song_tweet.format(song.title, song.id)
            twitterManager.postTweet(tweet)

    for song in added_songs:
        s = Song(song.video_id, song.title, "")
        dbManager.insert_video_playlist(s, db_playlist)
        if db_playlist.twitter_alert: 
            tweet = added_song_tweet.format(s.title, s.id)
            twitterManager.postTweet(tweet)

def check_songs_availability():
    songs = dbManager.get_all_songs()
    for song in songs:
        try:
            YouTube(YOUTUBE_VIDEO_URL + song.id).check_availability()
        except exceptions.VideoUnavailable:
            tweet = SONG_BECAME_UNAVAILABLE_TWEET.format(song.title, song.id)
            twitterManager.postTweet(tweet)
            dbManager.delete_song(song)

def download_song(song):
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
        
def download_songs():
    uncommited_songs = find_uncommited_songs()
    for song in uncommited_songs:
        logger.info("Downloading song " + song.title)
        download_song(song)
        filename = find_song_file()
        dbManager.set_filename(song.id, filename)
        gdriveManager.upload_file(filename)
        os.remove(filename)

def database_exists():
    for file in os.listdir("."):
        if file == dbManager.db_name:
            if os.stat(file).st_size != 0:
                return True
    return False

def find_song_file():
    for file in os.listdir("."):
        if file.endswith(FILE_EXTENSION):
            return file

def find_uncommited_songs():
    db_songs = dbManager.get_all_songs()
    gdrive_songs = gdriveManager.get_all_file_titles()
    db_songs_aux = db_songs.copy()
    for db_song in db_songs:
        for gdrive_song in gdrive_songs:
            if db_song.filename == gdrive_song:
                db_songs_aux.remove(db_song)
                break

    return db_songs_aux 

def track_playlist_changes():
    playlists = dbManager.get_playlists()
    for playlist in playlists:
        logger.info(f"Scanning playlist {playlist.title}...")
        handle_lists(playlist)
        

def backup_db():
    filename = dbManager.generate_sql_backup()
    gdriveManager.upload_backup(filename)

### BEGIN ###

n_hours = 24
while True:
    track_playlist_changes()
    download_songs()
    if n_hours == 24:
        n_hours = 0
        check_songs_availability()
        backup_db()
    n_hours += 1
    sleep(ONE_HOUR)