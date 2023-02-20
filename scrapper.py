from selenium import webdriver
from selenium.webdriver.common.by import By
from dbmanager import DBManager
from gdrivemanager import GDriveManager
import time
import re



print("HELLO WORLD")

dbManager = DBManager()
gdriveManager = GDriveManager()

def get_actual_videoids(url, ocultos):
    browser = webdriver.Edge()
    browser.maximize_window()
    browser.get(url)

    browser.find_element(By.CSS_SELECTOR, "button[aria-label = 'Aceptar todo']").click()
    time.sleep(2)
    if ocultos:
        element = browser.find_element(By.CSS_SELECTOR, "button[aria-label=\"Menú de acciones\"]")
        browser.execute_script("arguments[0].click();", element)
        print("ok")
        browser.find_element(By.LINK_TEXT, "Mostrar vídeos no disponibles").click()

    for _ in range (0, 10):
        browser.execute_script("var scrollingElement = (document.scrollingElement || document.body);scrollingElement.scrollTop = scrollingElement.scrollHeight;")
        time.sleep(2)
          # further code below

    youtube_elements = browser.find_elements(By.ID, "video-title")
    links = [elem.get_attribute('href') for elem in youtube_elements]
    youtube_ids = []
    for link in links:
        if link != None:
            n_index = link.index("&")
            youtube_ids.append(link[32:n_index])

    return youtube_ids

def get_db_videoids():
    ids = []
    songs = dbManager.get_all_songs()
    for song in songs:
        ids.append(song.id)

    return ids

def get_files_videoids():
    filetitles = gdriveManager.get_all_file_titles()
    for index, value in enumerate(filetitles):
        if value != "Lost and Found" and value != "DB Backups" and value != "27chart.db":
            m = re.findall(r"\[([A-Za-z0-9_-]+)\]", value)
            filetitles[index] = m[len(m) -1]  
    return filetitles

def get_youtube_videoids():
    playlists = dbManager.get_playlists()
    all_yt_videoids = []
    for playlist in playlists:
        all_yt_videoids += get_actual_videoids("https://www.youtube.com/playlist?list=" + playlist.id, False)
        print(f"Playlist: {playlist} scrapped")

    return all_yt_videoids

def get_hidden_playlist_videos(url):
    list_without_hidden = get_actual_videoids(url, False)
    list_with_hidden = get_actual_videoids(url, True)
    return set(list_with_hidden).difference(list_without_hidden)


print(get_hidden_playlist_videos("https://www.youtube.com/playlist?list=PLaJq2Gw03EijUkrVadSIA9Gxll7ewZ4oY"))
"""    
youtube_videoids = get_youtube_videoids()
files_videoids = get_files_videoids()
db_videoids = get_db_videoids()


result = set(youtube_videoids).difference(files_videoids)
result2 = set(youtube_videoids).difference(db_videoids)
result3 = set(db_videoids).difference(youtube_videoids)
result4 = set(db_videoids).difference(files_videoids)
result5 = set(files_videoids).difference(db_videoids)
result6 = set(files_videoids).difference(youtube_videoids)
print(result)
print("---")
print(result2)
print("---")
print(result3)
print("---")
print(result4)
print("---")
print(result5)
print("---")
print(result6)
print("---")

"""

    