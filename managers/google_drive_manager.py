from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
from common.utils import debug_mode

class GoogleDriveManager():
    def __init__(self):
        gauth = GoogleAuth()
        gauth.LoadClientConfigFile(os.getenv('GDRIVE_CLIENT_SECRET_PATH'))
        gauth.LoadCredentialsFile(os.getenv('GDRIVE_CREDENTIALS_PATH'))
        self.songs_folder_id = os.getenv('GDRIVE_SONGS_PATH')
        self.db_backups_folder_id = os.getenv('GDRIVE_BACKUPS_PATH')
        self.drive = GoogleDrive(gauth)

    def get_all_files(self):
        files = []
        files = self.drive.ListFile({'q': f"'{self.songs_folder_id}' in parents and trashed=false"}).GetList()
        
        return files

    def search_filename(self, song_id):
        all_files = self.get_all_files()
        for file in all_files:
            filename = file['title']
            if song_id in filename:
                return file['title']
        return None

    def upload_file(self, filename):
        if not debug_mode():
            file = self.drive.CreateFile({'parents': [{'id': self.songs_folder_id}]})
            file.SetContentFile(filename)
            file.Upload()

    def upload_backup(self, filename):
        if not debug_mode():
            file = self.drive.CreateFile({'parents': [{'id': self.db_backups_folder_id}]})
            file.SetContentFile(filename)
            file.Upload()
            
