from flask_httpauth import HTTPBasicAuth
from .database import my_db
from .usermodule.models import User


class MyBasicAuth:
    def __init__(self, db=None):
        self.auth = HTTPBasicAuth()
        self.db = db

    def set_db(self, db):
        self.db = db

    def read_user_by_username(self, username: str) -> User:
        result = self.db.session.query(User).filter(User.username == username).first()
        return result


auth_system = MyBasicAuth(my_db)


@auth_system.auth.verify_password
def verify_password(username, password):
    """ Функция проверки аутентификации пользователя """
    result = auth_system.read_user_by_username(username)
    if result is None:
        return None
    if result.password == password:
        return username
