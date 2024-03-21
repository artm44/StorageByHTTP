from flask import Flask, request, send_from_directory, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

from file_utils import *
from auth_utils import auth_system
from database import Metadata, User, StorageDB, my_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metadata.db'

db = StorageDB(my_db, app)
auth_system.set_db(db)
auth = auth_system.auth

UPLOAD_FOLDER = 'store'

SWAGGER_URL = '/swagger'  # URL for exposing Swagger UI
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "StorageByHTTP"
    }
)

app.register_blueprint(swaggerui_blueprint)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/register', methods=['POST'])
def register_user():
    try:
        username = request.args.get('username')
        password = request.args.get('password')
    except KeyError:
        return jsonify({'error': 'Not enough data'})

    if db.read_user_by_username(username) is not None:
        return jsonify({'error': 'Already there is user with this username'})

    if not db.upload_user(User(username=username, password=password)):
        return jsonify({'error': 'An error occurred while registration'})

    return jsonify({'message': 'success registration'})


@app.route('/unsubscribe', methods=['DELETE'])
@auth.login_required
def delete_user():
    user: User = db.read_user_by_username(auth.current_user())
    if not db.delete_user(user):
        return jsonify({'error': 'An error occurred while delete user'})
    return jsonify({'message': 'success'})


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
        if not db.upload_metadata(Metadata(username=auth.current_user(), file_hash=file_hash)):
            return jsonify({'error': 'An error occurred while adding the file'})
        subdir = os.path.join(UPLOAD_FOLDER, file_hash[:2])
        os.makedirs(subdir, exist_ok=True)
        file.save(file_path)
    else:
        # Проверка на наличие такого же файла у пользователя
        if not auth.current_user() in db.get_users_by_hash(file_hash):
            if not db.upload_metadata(Metadata(username=auth.current_user(), file_hash=file_hash)):
                return jsonify({'error': 'An error occurred while adding the file'})

    return jsonify({'hash': file_hash})


@app.route('/delete', methods=['DELETE'])
@auth.login_required
def delete_file():
    hash_to_delete = request.args.get('hash')

    if not allowed_hash(hash_to_delete):
        return jsonify({'error': 'Bad hash'})

    file_path = find_file_by_prefix(os.path.join(UPLOAD_FOLDER,
                                                 hash_to_delete[:2]), hash_to_delete)

    if file_path is not None:
        users = db.get_users_by_hash(hash_to_delete)
        if auth.current_user() in users:
            if db.delete_metadata(Metadata(username=auth.current_user(), file_hash=hash_to_delete)):
                if len(users) == 1:  # Если это был последний пользователь для файла
                    os.remove(file_path)
                return jsonify({'message': 'File deleted successfully'})
            else:
                return jsonify({'error': 'An error occurred while deleting the file'})
        else:
            return jsonify({'error': 'You can\'t delete this file'})
    else:
        return jsonify({'error': 'File not found'})


@app.route('/download', methods=['GET'])
def download_file():
    try:
        hash_to_download = request.args.get('hash')
    except KeyError:
        return jsonify({'error': 'No hash'})

    if not allowed_hash(hash_to_download):
        return jsonify({'error': 'Bad hash'})

    file_path = find_file_by_prefix(os.path.join(UPLOAD_FOLDER,
                                                 hash_to_download[:2]), hash_to_download)

    if file_path is not None:
        return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path),
                                   as_attachment=True)  # Возвращает файл для загрузки
    else:
        return jsonify({'error': 'File not found'})


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
