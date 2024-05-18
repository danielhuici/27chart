from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
from debug import DEBUG_MODE

class GDriveManager():
    def __init__(self):
        gauth = GoogleAuth()
        gauth.LoadClientConfigFile(os.getenv('GDRIVE_CLIENT_SECRET_PATH'))
        gauth.LoadCredentialsFile(os.getenv('GDRIVE_CREDENTIALS_PATH'))
        self.songs_folder_id = os.getenv('GDRIVE_SONGS_PATH')
        self.db_backups_folder_id = os.getenv('GDRIVE_BACKUPS_PATH')
        self.drive = GoogleDrive(gauth)

    def get_all_file_titles(self):
        file_titles = []
        files = self.drive.ListFile({'q': f"'{self.songs_folder_id}' in parents and trashed=false"}).GetList()
        for file in files:
            file_titles.append(file['title'])
        
        return file_titles

    def upload_file(self, filename):
        if not DEBUG_MODE:
            file = self.drive.CreateFile({'parents': [{'id': self.songs_folder_id}]})
            file.SetContentFile(filename)
            file.Upload()

    def upload_backup(self, filename):
        if not DEBUG_MODE:
            file = self.drive.CreateFile({'parents': [{'id': self.db_backups_folder_id}]})
            file.SetContentFile(filename)
            file.Upload()

    
