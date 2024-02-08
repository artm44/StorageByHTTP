import os
import json
import hashlib
from typing import Dict, Any

# Пример расширений файлов 
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py'}


def hash_file_contents(file) -> str:
    """ Функция хэширования файла по его содержимому """
    hasher = hashlib.md5()
    for chunk in iter(lambda: file.read(4096), b''):
        hasher.update(chunk)
    file.seek(0)
    return hasher.hexdigest()

def allowed_file(filename) -> bool:
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_metadata(file_path, metadata) -> None:
    """ Функция сохранения метаданных о файле """
    metadata_file = file_path + ".metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f)

def get_metadata(file_path) -> ( Dict[str, Any] | None):
    """ Функция получения метаданных о файле """
    metadata_file = file_path + ".metadata.json"
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            return json.load(f)
    else:
        return None

def file_belongs_to_user(file_path, username) -> bool:
    """ Функция проверки принаждежности файла пользователю """
    metadata = get_metadata(file_path)
    if metadata and 'owner' in metadata:
        return metadata['owner'] == username
    else:
        return False
    
def find_file_by_prefix(directory, prefix):
    if not os.path.isdir(directory):
        return None
    for filename in os.listdir(directory):
        if filename.startswith(prefix) and os.path.isfile(os.path.join(directory, filename)):
            return os.path.join(directory, filename)
        
def exist_file_by_prefix(directory, prefix):
    if find_file_by_prefix(directory, prefix) is None: return False
    else: return True

