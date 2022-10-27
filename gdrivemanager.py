from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from debug import DEBUG_MODE

SONGS_FOLDER_ID = "1ohudHRKbA3XcmvODZA9FvViuwwhiu7aO"
DB_BACKUPS_FOLDER_ID = "1Q1rtb2ghMAVYvt6aQbmPiOR74u4fv7ia"

class GDriveManager():
    def __init__(self):
        self.drive = GoogleDrive(GoogleAuth())

    def get_all_file_titles(self):
        file_titles = []
        files = self.drive.ListFile({'q': f"'{SONGS_FOLDER_ID}' in parents and trashed=false"}).GetList()
        for file in files:
            file_titles.append(file['title'])
        
        return file_titles

    def upload_file(self, filename):
        if not DEBUG_MODE:
            file = self.drive.CreateFile({'parents': [{'id': SONGS_FOLDER_ID}]})
            file.SetContentFile(filename)
            file.Upload()

    def upload_backup(self, filename):
        if not DEBUG_MODE:
            file = self.drive.CreateFile({'parents': [{'id': DB_BACKUPS_FOLDER_ID}]})
            file.SetContentFile(filename)
            file.Upload()

    
