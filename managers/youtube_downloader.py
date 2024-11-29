from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
import os
import logging

YOUTUBE_VIDEO_BASEURL = "https://www.youtube.com/watch?v="

class YoutubeDownloader():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ydlp_opts = {
            'quiet': False,
            'no_warnings': False,
        }

    def download_song(self, song):
        ydl_opts =  self.ydlp_opts | {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try: 
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download(YOUTUBE_VIDEO_BASEURL + song.id)
        except DownloadError as error:
            self.logger.warning(f"Couldn't download song {song} ({error}). \nTrying to download it using proxy...")
            ydl_opts.update({'proxy': os.getenv('FALLBACK_PROXY_URL')})

            try: 
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download(YOUTUBE_VIDEO_BASEURL + song.id)
                    return True
            except DownloadError:
                self.logger.error(f"Can't download song {song}") 
                return False

    def check_video_availability(self, song):
        ydl_opts =  self.ydlp_opts | {
            'extract_flat': True,
            'ignoreerrors': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            video = ydl.extract_info(song.id, download=False)
            if video is not None and (video['availability'] == "public" or video['availability'] == 'needs_auth'):
                return True
            return False