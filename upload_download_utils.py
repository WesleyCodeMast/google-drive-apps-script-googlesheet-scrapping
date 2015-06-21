from pydrive.auth import GoogleAuth 
from pydrive.drive import GoogleDrive

gauth = GoogleAuth() 
drive = GoogleDrive(gauth)

def upload2drive(file_path, folder_id):
    gfile = drive.CreateFile({'parents': [{'id': folder_id}]})

    gfile.SetContentFile(file_path)

    gfile.Upload()