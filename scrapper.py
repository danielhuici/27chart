from selenium import webdriver
from selenium.webdriver.common.by import By
from managers.db_manager import DBManager
from managers.google_drive_manager import GoogleDriveManager
from managers.youtube_scrapper import YoutubeScrapper
import time
import re
from dotenv import load_dotenv

def get_db_videoids():
    ids = []
    songs = dbManager.get_all_songs()
    for song in songs:
        ids.append(song.id)

    return ids

def get_files_videoids():
    files = gdriveManager.get_all_files()
    file_ids = set()
    pattern = r'\[([^\]]+)\](?=[^[\]]*\.mp3$)'
    for file in files:
        if file['title'] not in ["Lost and Found", "DB Backups", "27chart.db"]:
            match = re.search(pattern, file['title'])
            if match:
                file_ids.add(match.group(1))
    
    return file_ids

def get_youtube_videoids():
    scrapper = YoutubeScrapper()
    playlists = dbManager.get_playlists()
    all_yt_videoids = set()
    for playlist in playlists:
        _, videos = scrapper.get_available_playlist_videos(playlist.id)
        for video in videos:
            all_yt_videoids.add(video.id)
        print(f"Playlist: {playlist} scrapped")

    return all_yt_videoids

def get_file_id(title):
    pattern = r'\[([^\]]+)\](?=[^[\]]*\.mp3$)'
    if title not in ["DB Backups", "Lost and Found", "27chart.db"]:
        match = re.search(pattern, title)
        if match:
            return match.group(1)
        else:
            raise Exception

def find_gdrive_duplicates():
    files = gdriveManager.get_all_files()
    duplicate_files = {}
    duplicate_objects = []
    all_ids = set()
    for file in files:
        title = file['title']
        file_id = get_file_id(title)
        if file_id in all_ids:
            duplicate_files[file_id] = title
            duplicate_objects.append(file)
        else:
            all_ids.add(file_id)

    print(f"Duplicate objects: {len(duplicate_objects)}")
    print(f"Duplicate files: {len(duplicate_files)}")
    if len(duplicate_objects) > 0:
        remove_duplicates(duplicate_objects)
    else:
        print("No duplicate files found")

    return duplicate_files, duplicate_objects

def remove_duplicates(duplicate_objects):
    result = input("WARNING: Duplicate files will be removed. Do you want to continue? (Y/n): ")
    if result in ["Y", "y"]:
        for object in duplicate_objects:
            object.Trash()
        print("Duplicate objects removed")

if __name__:
    print("HELLO WORLD")
    load_dotenv()

    dbManager = DBManager()
    gdriveManager = GoogleDriveManager()

    find_gdrive_duplicates()

    db_videoids = get_db_videoids()
    files_videoids = get_files_videoids()
    youtube_videoids = get_youtube_videoids()

    result = set(youtube_videoids).difference(files_videoids)
    result2 = set(youtube_videoids).difference(db_videoids)
    result3 = set(db_videoids).difference(youtube_videoids)
    result4 = set(db_videoids).difference(files_videoids)
    result5 = set(files_videoids).difference(db_videoids)
    result6 = set(files_videoids).difference(youtube_videoids)
    print(f"Vídeos en YouTube pero no en Google Drive: {len(result)}")
    print(result)
    print("-----------------------------------------")
    print(f"Vídeos en YouTube pero no en Base de Datos: {len(result2)}")
    print(result2)
    print("-----------------------------------------")
    print(f"Vídeos en Base de Datos pero no en YouTube: {len(result3)}")
    print(result3)
    print("-----------------------------------------")
    print(f"Vídeos en Base de Datos pero no en Google Drive: {len(result4)}")
    print(result4)
    print("-----------------------------------------")
    print(f"Vídeos en Google Drive pero no en Base de Datos: {len(result5)}")
    print(result5)
    print("-----------------------------------------")
    print(f"Vídeos en Google Drive pero no en YouTube: {len(result6)}")
    print(result6)
    print("---")

