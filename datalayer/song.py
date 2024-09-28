

class Song():
    def __init__(self, id, title, filename=""):
        self.id = id
        self.title = title
        self.filename = filename

    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return f"[{self.id}] {self.title} ({self.filename})"