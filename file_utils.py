import os
import hashlib

# Пример расширений файлов 
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py'}


def hash_file_contents(file) -> str:
    """ Функция хэширования файла по его содержимому """
    hasher = hashlib.sha256()
    for chunk in iter(lambda: file.read(4096), b''):
        hasher.update(chunk)
    file.seek(0)
    return hasher.hexdigest()


def allowed_file(filename: str) -> bool:
    """ Функция проверки расширения файла """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_hash(hash_value: str) -> bool:
    """ Функция проверки значения хэша """
    for char in hash_value:
        if (char < '0' or char > '9') and (char < 'a' or char > 'f'):
            return False
    return True


def find_file_by_prefix(directory: str, prefix: str) -> str:
    """ Функция поиска файла по хэшу """
    if not os.path.isdir(directory):
        return None
    for filename in os.listdir(directory):
        if filename.startswith(prefix) and os.path.isfile(os.path.join(directory, filename)):
            return os.path.join(directory, filename)


def exist_file_by_prefix(directory: str, prefix: str) -> bool:
    """ Функция проверки существования файла по хэшу """
    if find_file_by_prefix(directory, prefix) is None:
        return False
    else:
        return True
