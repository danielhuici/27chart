
class Playlist():
    def __init__(self, id, title, notify):
        self.id = id
        self.title = title
        self.notify = notify
        self.songs = []
    
    def add_song(self, song):
        self.songs.append(song)

    def __eq__(self, id):
        return self.id == id

    def __str__(self):
        return f"{self.id} - {self.title}"