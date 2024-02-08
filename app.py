from flask import Flask, request, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from file_utils import *
from auth_utils import auth


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metadata.db'
db = SQLAlchemy(app)

class Metadata(db.Model):
    __tablename__ = 'metadata'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    file_hash = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, file_hash):
        self.username = username
        self.file_hash = file_hash

    def __repr__(self) -> str:
        return 'Metadata %r' % self.id

def upload_metadata(metadata):
    db.session.add(metadata)
    db.session.commit()
    
def delete_metadata(metadata):
    result = db.session.query(Metadata).filter(Metadata.file_hash == metadata.file_hash, \
                                                    Metadata.username == metadata.username).first()
    db.session.delete(result)
    db.session.commit()
    
def get_users_by_hash(file_hash):
    result = db.session.query(Metadata).filter(Metadata.file_hash == file_hash).all()
    if result:
        return [data.username for data in result]
    else:
        return None

UPLOAD_FOLDER = 'store'


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

    extension = file.filename[file.filename.rfind('.'):]
    file_hash = hash_file_contents(file)
    file_path = os.path.join(UPLOAD_FOLDER, file_hash[:2], file_hash + extension)

    if not exist_file_by_prefix(os.path.join(UPLOAD_FOLDER, \
                                                  file_hash[:2]), file_hash):
        subdir = os.path.join(UPLOAD_FOLDER, file_hash[:2])
        os.makedirs(subdir, exist_ok=True)
        file.save(file_path)

        try:
            upload_metadata(Metadata(username=auth.current_user(), file_hash=file_hash))
        except:
            os.remove(file_path)
            return jsonify({'error': 'An error occurred while adding the file'})
    else:
        if not auth.current_user() in get_users_by_hash(file_hash):
            try:
                upload_metadata(Metadata(username=auth.current_user(), file_hash=file_hash))
            except:
                return jsonify({'error': 'An error occurred while adding the file'})

    return jsonify({'hash': file_hash})

@app.route('/delete', methods=['DELETE'])
@auth.login_required
def delete_file():
    hash_to_delete = request.args.get('hash')
    file_path = find_file_by_prefix(os.path.join(UPLOAD_FOLDER, \
                                                  hash_to_delete[:2]), hash_to_delete)
    
    if not file_path is None:
        users = get_users_by_hash(hash_to_delete)
        print(users)
        if  auth.current_user() in users:
            try:
                delete_metadata(Metadata(username=auth.current_user(), file_hash=hash_to_delete))
                if len(users) == 1:
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
