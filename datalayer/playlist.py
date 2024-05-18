
class Playlist():
    def __init__(self, id, title, twitter_alert):
        self.id = id
        self.title = title
        self.twitter_alert = twitter_alert
        self.songs = []
    
    def add_song(self, song):
        self.songs.append(song)