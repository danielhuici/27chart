from dbmanager import DBManager
from pytube import Playlist, YouTube, exceptions

YOUTUBE_PLAYLIST_URL = "https://www.youtube.com/playlist?list="

def track_playlist_changes():	
	print(YouTube("https://www.youtube.com/watch?v=CyT-DaI0rqQ").title) 
	print(YouTube("https://www.youtube.com/watch?v=JIoj1RYvz1Y").title) 
	print(YouTube("https://www.youtube.com/watch?v=YntDxln7w5U").title) 

dbManager = DBManager()
track_playlist_changes()