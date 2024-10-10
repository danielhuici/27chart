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
import re

from datalayer.song import Song

N_VIDEOS_CSS_SELECTOR = "#page-manager > ytd-browse > ytd-playlist-header-renderer \
                         > div > div.immersive-header-content.style-scope.ytd-playlist-header-renderer \
                         > div.thumbnail-and-metadata-wrapper.style-scope.ytd-playlist-header-renderer \
                         > div > div.metadata-action-bar.style-scope.ytd-playlist-header-renderer \
                         > div.metadata-text-wrapper.style-scope.ytd-playlist-header-renderer \
                         > ytd-playlist-byline-renderer > div > yt-formatted-string:nth-child(2) \
                         > span:nth-child(1)"

YOUTUBE_PLAYLIST_BASEURL = "https://www.youtube.com/playlist?list="
ACCEPT_ERROR = 20 # We accept 20 videos of error between actual number of videos and retrieved items

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

    def _get_actual_n_videos(self, driver):
        el = driver.find_element("tag name", "body")
        n_videos_text = re.search(r'\d+ videos', el.text).group()
        n_videos = n_videos_text.split(" ")[0]
        return int(n_videos)

    def _scraper_scroll_playlist(self, driver):
        last_height = driver.execute_script("return document.documentElement.scrollHeight")

        try:
            while True:
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(3)
                new_height = driver.execute_script("return document.documentElement.scrollHeight")
                if new_height == last_height:
                    break  

                last_height = new_height
        except TimeoutException as e:
            self.logger.warning(f"Timeout while scrolling playlist: {e}")

    def _accept_agreement(self, driver):
        accept_button = WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Accept all']"))
                )
        accept_button.click()

    def _get_all_video_elements(self, driver):
        video_list_element = WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id=\"contents\"]/ytd-item-section-renderer[1]")))
        self._scraper_scroll_playlist(driver)
        video_elements = video_list_element.find_elements(By.ID, "video-title")
        return video_elements

    def _check_consistency(self, actual_n_videos, retrived_n_videos):
        return (actual_n_videos - retrived_n_videos) < ACCEPT_ERROR
    
    def _obtain_song_list(self, video_elements):
        songs = []
        for video_element in video_elements:
            video_url = video_element.get_attribute('href')
            parsed_url = urlparse(video_url)
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('v', [None])[0]
            video_title = video_element.text
            songs.append(Song(video_id, video_title))

        return songs
    
    def get_available_playlist_videos(self, playlist_id):
        songs = []
        try:
            with self._scraper_session() as driver:
                driver.get(f"{YOUTUBE_PLAYLIST_BASEURL}{playlist_id}")
                self._accept_agreement(driver)
                actual_n_videos = self._get_actual_n_videos(driver)
                video_elements = self._get_all_video_elements(driver)
                if self._check_consistency(actual_n_videos, len(video_elements)):
                    songs = self._obtain_song_list(video_elements)
                    return True, songs
                self.logger.warning(f"Big inconsistency while scrapping playlist {playlist_id} (Actual videos: {actual_n_videos} Retrieved videos: {len(video_elements)})")
                return False, []
            
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.warning(f"Error while scraping playlist {playlist_id}: {e}")
            return False, []
    