from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
import os
import logging
from datalayer.song import Song

YOUTUBE_VIDEO_BASEURL = "https://www.youtube.com/watch?v="
N_ATTEMPS = 2

class YoutubeDownloader():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ydlp_opts = {
            'quiet': False,
            'no_warnings': False,
            'proxy': os.getenv('FALLBACK_PROXY_URL'),
            
            #'proxy': 'socks5://gc.huici.es:25288'
        }

    def download_song(self, song):
        ydl_opts = {
            **self.ydlp_opts,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        for attempt in range(N_ATTEMPS):
            try: 
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download(YOUTUBE_VIDEO_BASEURL + song.id)
                    return True
            except DownloadError as error:
                if attempt == 0:
                    self.logger.warning(f"Couldn't download song {song} ({error}). Trying with proxy...")
                    ydl_opts['proxy'] = os.getenv('FALLBACK_PROXY_URL')
                else:
                    self.logger.error(f"Can't download song {song}")
                    return False
                
    def check_video_availability(self, song):
        ydl_opts = {
            **self.ydlp_opts,
            'extract_flat': True,
            'ignoreerrors': True
        }

        for attempt in range(N_ATTEMPS):
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    video = ydl.extract_info(song.id, download=False)
                    if video is not None and video['availability'] in ["public", "needs_auth"]:
                        return True
                    self.logger.debug(f"Video availability: {video}")
                    return False
            except DownloadError as error:
                if attempt == 0:
                    self.logger.warning(f"Couldn't check song availability {song} ({error}). Trying with fallback proxy...")
                    ydl_opts['proxy'] = os.getenv('FALLBACK_PROXY_URL')
                else:
                    self.logger.error(f"Can't check video availability {song}")
                    return False
                
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    youtubedownloader = YoutubeDownloader()
    youtubedownloader.check_video_availability(Song("x8G4xrYfWmw", "Title", "Filenames"))
