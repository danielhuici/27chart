from selenium import webdriver
from selenium.webdriver.common.by import By
from dbmanager import DBManager
import time

print("HELLO WORLD")

dbManager = DBManager()

def get_actual_videoids(url, ocultos):
    browser = webdriver.Edge()
    browser.maximize_window()
    browser.get(url)

    browser.find_element(By.CSS_SELECTOR, "button[aria-label = 'Aceptar todo']").click()
    time.sleep(2)
    if ocultos:
        browser.find_element(By.CSS_SELECTOR, "button[aria-label = 'Menú de acciones']").click()
        browser.find_element(By.LINK_TEXT, "Mostrar vídeos no disponibles").click()

    for _ in range (0, 10):
        browser.execute_script("var scrollingElement = (document.scrollingElement || document.body);scrollingElement.scrollTop = scrollingElement.scrollHeight;")
        time.sleep(2)
          # further code below

    youtube_elements = browser.find_elements(By.ID, "video-title")
    links = [elem.get_attribute('href') for elem in youtube_elements]
    youtube_ids = []
    for link in links:
        n_index = link.index("&")
        youtube_ids.append(link[32:n_index])

    return youtube_ids

def get_db_videoids():
    ids = []
    songs = dbManager.get_all_songs()
    for song in songs:
        ids.append(song.id)

    return ids

all_yt_videoids = get_actual_videoids("https://www.youtube.com/playlist?list=PLaJq2Gw03Eigv6RQqXKmUP8lPO3IoXbEl", False)

for id in all_yt_videoids:
    if id == "h9wualcJuE4":
        print("ESTÁ")

#print(all_yt_videoids)
#print("-----")
#result = set(all_yt_videoids).difference(get_db_videoids())
#print(result)


    