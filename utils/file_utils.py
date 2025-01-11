import os

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_file(file_path, file_name):
    with open(os.path.join(UPLOAD_FOLDER, file_name), 'wb') as new_file:
        new_file.write(file_path.read())