from flask import Blueprint, request, jsonify

from .models import User, UserDB, my_db
from app.auth import auth_system

auth = auth_system.auth

UPLOAD_FOLDER = 'store'

module = Blueprint('user', __name__, url_prefix='/users')

db = UserDB(my_db)


@module.route('/register', methods=['POST'])
def register_user():
    try:
        username = request.args.get('username')
        password = request.args.get('password')
    except KeyError:
        return jsonify({'error': 'Not enough data'}), 400

    if db.read_user_by_username(username) is not None:
        return jsonify({'error': 'Already there is user with this username'}), 400

    if not db.upload_user(User(username=username, password=password)):
        return jsonify({'error': 'An error occurred while registration'}), 500

    return jsonify({'message': 'success registration'}), 200


@module.route('/unsubscribe', methods=['DELETE'])
@auth.login_required
def delete_user():
    user: User = db.read_user_by_username(auth.current_user())
    if not db.delete_user(user):
        return jsonify({'error': 'An error occurred while delete user'}), 500
    return jsonify({'message': 'success'}), 200
