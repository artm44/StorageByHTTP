from flask import Flask, request, send_from_directory, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import os
from file_utils import *
from auth_utils import auth
from database import Metadata, MetadataDB, my_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metadata.db'
db = MetadataDB(my_db, app)

UPLOAD_FOLDER = 'store'

SWAGGER_URL = '/swagger'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.json'

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "StorageByHTTP"
    }
)

app.register_blueprint(swaggerui_blueprint)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if not allowed_file(file.filename):
        return jsonify({'error': 'Bad file extension'})

    last_dot = file.filename.rfind('.')
    extension = file.filename[last_dot:] if last_dot != -1 else ''
    file_hash = hash_file_contents(file)
    file_path = os.path.join(UPLOAD_FOLDER, file_hash[:2], file_hash + extension)

    # Проверка существования файла
    if not exist_file_by_prefix(os.path.join(UPLOAD_FOLDER, file_hash[:2]), file_hash):
        subdir = os.path.join(UPLOAD_FOLDER, file_hash[:2])
        os.makedirs(subdir, exist_ok=True)
        file.save(file_path)

        try:
            db.upload_metadata(Metadata(username=auth.current_user(), file_hash=file_hash))
        except:
            os.remove(file_path)
            return jsonify({'error': 'An error occurred while adding the file'})
    else:
        # Проверка на наличие такого же файла у пользователя
        if not auth.current_user() in db.get_users_by_hash(file_hash):
            try:
                db.upload_metadata(Metadata(username=auth.current_user(), file_hash=file_hash))
            except:
                return jsonify({'error': 'An error occurred while adding the file'})

    return jsonify({'hash': file_hash})


@app.route('/delete', methods=['DELETE'])
@auth.login_required
def delete_file():
    hash_to_delete = request.args.get('hash')
    file_path = find_file_by_prefix(os.path.join(UPLOAD_FOLDER,
                                                 hash_to_delete[:2]), hash_to_delete)

    if not file_path is None:
        users = db.get_users_by_hash(hash_to_delete)
        if auth.current_user() in users:
            try:
                db.delete_metadata(Metadata(username=auth.current_user(), file_hash=hash_to_delete))
                if len(users) == 1:  # Если это был последний пользователь для файла
                    os.remove(file_path)
                return jsonify({'message': 'File deleted successfully'})
            except:
                return jsonify({'error': 'An error occurred while deleting the file'})
        else:
            return jsonify({'error': 'You can\'t delete this file'})
    else:
        return jsonify({'error': 'File not found'})


@app.route('/download', methods=['GET'])
def download_file():
    hash_to_download = request.args.get('hash')
    file_path = find_file_by_prefix(os.path.join(UPLOAD_FOLDER, \
                                                 hash_to_download[:2]), hash_to_download)

    if not file_path is None:
        return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path), \
                                   as_attachment=True)  # Возвращает файл для загрузки
    else:
        return jsonify({'error': 'File not found'})


if __name__ == '__main__':
    app.run(debug=True)
