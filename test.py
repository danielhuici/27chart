from dbmanager import DBManager
from pytube import Playlist, YouTube, exceptions
from gdrivemanager import GDriveManager
from twittermanager import TwitterManager
import logging
YOUTUBE_PLAYLIST_URL = "https://www.youtube.com/playlist?list="

def track_playlist_changes():	
	print(YouTube("https://www.youtube.com/watch?v=CyT-DaI0rqQ").title) 
	print(YouTube("https://www.youtube.com/watch?v=JIoj1RYvz1Y").title) 
	print(YouTube("https://www.youtube.com/watch?v=YntDxln7w5U").title) 
	print("------")
	info = YouTube("https://www.youtube.com/watch?v=zvsJe-J1aK8").metadata
	print(info)
	#print(f"{title} - {artist}")

logger = logging.getLogger(__name__)
db = DBManager()
print(db.get_playlists())
twitter = TwitterManager(logger)
twitter.post_tweet("test")