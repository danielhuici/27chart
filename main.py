import dbm
from gettext import find
import logging
import os
import sys
from sqlite3 import connect
from time import sleep
from pytube import Playlist, YouTube, exceptions
from dbmanager import DBManager
from twittermanager import TwitterManager
from gdrivemanager import GDriveManager
from song import Song
from apscheduler.schedulers.blocking import BlockingScheduler



SETUP_FLAG = "--setup"
KIFIXO_27_CHART_NAME = "Kifixo 27 Chart"
KIFIXO_TOP_EVER_MUSIC_NAME = "Kifixo TOP-Ever Music"
KIFIXO_GRAND_RESERVA_NAME = "Kifixo Grand Reserva"
SALEN_LISTA_NAME = "Salen de la lista"
SALEN_LISTA_2_NAME = "Salen de la lista 2"
KIFIXO_27_CHART_DELETED_SONG_TWEET = "\U0000274C SALE DE LA LISTA #Kifixo27Chart \n {} \n youtu.be/{}"
KIFIXO_27_CHART_NEW_SONG_TWEET = "\U00002705 ENTRADA EN LISTA #Kifixo27Chart \n {} \n youtu.be/{}"
KIFIXO_TOP_EVER_DELETED_SONG_TWEET = "\U0001F51D \U0000274C SALIDA DE #KifixoTopEverMusic \n {} \n youtu.be/{}"
KIFIXO_TOP_EVER_NEW_SONG_TWEET = "\U0001F51D \U00002705 ENTRADA EN #KifixoTopEverMusic \n {} \n youtu.be/{}"
KIFIXO_GRAND_RESERVA_DELETED_SONG_TWEET = "\U0001F7E1 THANK YOU \U0001F7E1 \n Salida #KifixoGrandReserva y revelada para Kifixo 27 Chart \n {} \n youtu.be/{}"
KIFIXO_GRAND_RESERVA_NEW_SONG_TWEET = "\U00002B50 Congratulations \U00002B50 \n ENTRADA A #KifixoGrandReserva Y CANDIDATA A #KifixoSong2023 \n {} \n youtu.be/{}"
SONG_BECAME_UNAVAILABLE_TWEET = "\U00002757 Una canción ya no está disponible @kifixo23 \U00002757 \n {} \n"
YOUTUBE_PLAYLIST_URL = "https://www.youtube.com/playlist?list="
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v="
FILE_EXTENSION = ".mp4"


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
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

# Handle Kifixo27Chart, Kifixo Grand Reserva & Kifixo TOP-Ever Music playlists
def handle_main_lists(db_playlist):
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
    logger.info(str(len(retired_songs)) + " " + str(len(added_songs)))

    for song in retired_songs:
        dbManager.deattach_playlist_song(song, db_playlist)
        tweet = retired_song_tweet.format(song.title, song.id)
        twitterManager.postTweet(tweet)

    for song in added_songs:
        s = Song(song.video_id, song.title, "")
        dbManager.insert_video_playlist(s, db_playlist)
        tweet = added_song_tweet.format(s.title, s.id)
        twitterManager.postTweet(tweet)

def handle_salen_de_la_lista(db_playlist):
    p = Playlist(f'{YOUTUBE_PLAYLIST_URL}{db_playlist.id}')

    retired_songs, added_songs = find_playlist_changes(db_playlist, p.videos)
    for song in retired_songs:
        dbManager.deattach_playlist_song(song, db_playlist)

    for song in added_songs:
        dbManager.insert_video_playlist(song, db_playlist)

def check_songs_availability():
    songs = dbManager.get_all_songs()
    for song in songs:
        try:
            YouTube(YOUTUBE_VIDEO_URL + song.id).check_availability()
        except exceptions.VideoUnavailable:
            tweet = SONG_BECAME_UNAVAILABLE_TWEET.format(song.title, song.video_id)
            twitterManager.postTweet(tweet)

def download_song(song):
    video = YouTube(YOUTUBE_VIDEO_URL + song.id)
    video.streams.filter(only_audio=True).first().download()
    

def download_songs():
    uncommited_songs = find_uncommited_songs()
    for song in uncommited_songs:
        download_song(song)
        filename = find_song_file()
        dbManager.set_filename(song.id, filename)
        gdriveManager.upload_file(filename)
        os.remove(filename)

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
        if playlist.title == KIFIXO_27_CHART_NAME or playlist.title == KIFIXO_TOP_EVER_MUSIC_NAME or playlist.title == KIFIXO_GRAND_RESERVA_NAME:
            handle_main_lists(playlist)
        elif playlist.title == SALEN_LISTA_NAME or playlist.title == SALEN_LISTA_2_NAME:
            handle_salen_de_la_lista(playlist)


if len(sys.argv) > 1 and sys.argv[1] == SETUP_FLAG:
    logger.info("Setting up database...")
    dbManager.create_tables()
    playlists = dbManager.get_playlists()
    for playlist in playlists:
        p = Playlist(f'{YOUTUBE_PLAYLIST_URL}{playlist.id}')
        logger.info("Building playlist " + playlist.title)
        for video in p.videos:
            dbManager.insert_video_playlist(Song(video.video_id, video.title, ""), playlist)

    logger.info("Setup finished")
else:
    sheduler = BlockingScheduler(timezone="Europe/Madrid")
    sheduler.add_job(track_playlist_changes, 'interval', hours=1)
    sheduler.add_job(download_songs, 'interval', hours=1)
    sheduler.add_job(check_songs_availability, 'interval', hours=24)
    sheduler.start()


