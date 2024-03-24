from flask import Blueprint, request, jsonify, send_from_directory, send_file
import os

from .models import Metadata, MetadataDB, my_db
from .file_utils import *
from app.auth import auth_system

auth = auth_system.auth

UPLOAD_FOLDER = 'store'

module = Blueprint('file', __name__, url_prefix='/files')

db = MetadataDB(my_db)


@module.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Bad file extension'}), 400

    last_dot = file.filename.rfind('.')
    extension = file.filename[last_dot:] if last_dot != -1 else ''
    file_hash = hash_file_contents(file)
    file_path = os.path.join(UPLOAD_FOLDER, file_hash[:2], file_hash + extension)

    # Проверка существования файла
    if not exist_file_by_prefix(os.path.join(UPLOAD_FOLDER, file_hash[:2]), file_hash):
        if not db.upload_metadata(Metadata(username=auth.current_user(), file_hash=file_hash)):
            return jsonify({'error': 'An error occurred while adding the file'}), 500
        subdir = os.path.join(UPLOAD_FOLDER, file_hash[:2])
        os.makedirs(subdir, exist_ok=True)
        file.save(file_path)
    else:
        # Проверка на наличие такого же файла у пользователя
        if not auth.current_user() in db.get_users_by_hash(file_hash):
            if not db.upload_metadata(Metadata(username=auth.current_user(), file_hash=file_hash)):
                return jsonify({'error': 'An error occurred while adding the file'}), 500

    return jsonify({'hash': file_hash}), 200


@module.route('/delete', methods=['DELETE'])
@auth.login_required
def delete_file():
    hash_to_delete = request.args.get('hash')

    if not allowed_hash(hash_to_delete):
        return jsonify({'error': 'Bad hash'}), 400

    file_path = find_file_by_prefix(os.path.join(UPLOAD_FOLDER,
                                                 hash_to_delete[:2]), hash_to_delete)

    if file_path is not None:
        users = db.get_users_by_hash(hash_to_delete)
        if auth.current_user() in users:
            if db.delete_metadata(Metadata(username=auth.current_user(), file_hash=hash_to_delete)):
                if len(users) == 1:  # Если это был последний пользователь для файла
                    os.remove(file_path)
                return jsonify({'message': 'File deleted successfully'}), 200
            else:
                return jsonify({'error': 'An error occurred while deleting the file'}), 500
        else:
            return jsonify({'error': 'You can\'t delete this file'}), 400
    else:
        return jsonify({'error': 'File not found'}), 400


@module.route('/download', methods=['GET'])
def download_file():
    try:
        hash_to_download = request.args.get('hash')
    except KeyError:
        return jsonify({'error': 'No hash'}), 400

    if not allowed_hash(hash_to_download):
        return jsonify({'error': 'Bad hash'}), 400

    file_path = find_file_by_prefix(os.path.join(UPLOAD_FOLDER,
                                                 hash_to_download[:2]), hash_to_download)
    if file_path is not None:
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, file_path)
        return send_file(file_path, as_attachment=True), 200  # Возвращает файл для загрузки
    else:
        return jsonify({'error': 'File not found'}), 404
