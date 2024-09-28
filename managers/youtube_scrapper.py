from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urlparse, parse_qs
import time
from contextlib import contextmanager
import logging
import os

from datalayer.song import Song

N_VIDEOS_CSS_SELECTOR = "#page-manager > ytd-browse > ytd-playlist-header-renderer \
                         > div > div.immersive-header-content.style-scope.ytd-playlist-header-renderer \
                         > div.thumbnail-and-metadata-wrapper.style-scope.ytd-playlist-header-renderer \
                         > div > div.metadata-action-bar.style-scope.ytd-playlist-header-renderer \
                         > div.metadata-text-wrapper.style-scope.ytd-playlist-header-renderer \
                         > ytd-playlist-byline-renderer > div > yt-formatted-string:nth-child(2) \
                         > span:nth-child(1)"

YOUTUBE_PLAYLIST_BASEURL = "https://www.youtube.com/playlist?list="

class YoutubeScrapper():
    def __init__(self, driver_path="/usr/bin/chromedriver", timeout=15):
        self.driver_path = driver_path
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.selenium_host = os.getenv('SELENIUM_HOST')

    @contextmanager
    def _scraper_session(self):
        driver_options = Options()
        driver_options.add_argument("--headless")
        driver = webdriver.Remote(f'http://{self.selenium_host}', options=driver_options)
        driver.maximize_window()

        try:
            yield driver
        finally:
            driver.quit()

    def _scraper_scroll_playlist(self, driver):
        last_height = driver.execute_script("return document.documentElement.scrollHeight")

        try:
            while True:
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.documentElement.scrollHeight")
                if new_height == last_height:
                    break  

                last_height = new_height
        except TimeoutException as e:
            self.logger.warning(f"Timeout while scrolling playlist: {e}")

    def get_available_playlist_videos(self, playlist_id):
        songs = []
        try:
            with self._scraper_session() as driver:
                driver.get(f"{YOUTUBE_PLAYLIST_BASEURL}{playlist_id}")
                accept_button = WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Accept all']"))
                )
                accept_button.click()
                video_list_element = WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id=\"contents\"]/ytd-item-section-renderer[1]")))
                self._scraper_scroll_playlist(driver)
                video_elements = video_list_element.find_elements(By.ID, "video-title")

                for video_element in video_elements:
                    video_url = video_element.get_attribute('href')
                    parsed_url = urlparse(video_url)
                    query_params = parse_qs(parsed_url.query)
                    video_id = query_params.get('v', [None])[0]
                    video_title = video_element.text
                    songs.append(Song(video_id, video_title))

        except (TimeoutException, NoSuchElementException) as e:
            self.logger.warning(f"Error while scraping playlist {playlist_id}: {e}")

        return songs
    