from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

FOLDER_ID = "1ohudHRKbA3XcmvODZA9FvViuwwhiu7aO"

class GDriveManager():
    def __init__(self):
        self.drive = GoogleDrive(GoogleAuth())

    def get_all_file_titles(self):
        file_titles = []
        files = self.drive.ListFile({'q': f"'{FOLDER_ID}' in parents and trashed=false"}).GetList()
        for file in files:
            file_titles.append(file['title'])
        
        return file_titles

    def upload_file(self, filename):
        file = self.drive.CreateFile({'parents': [{'id': FOLDER_ID}]})
        file.SetContentFile(filename)
        file.Upload()

