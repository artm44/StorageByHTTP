from flask_httpauth import HTTPBasicAuth


class MyBasicAuth:
    def __init__(self):
        self.auth = HTTPBasicAuth()
        self.db = None

    def set_db(self, db):
        self.db = db


auth_system = MyBasicAuth()


@auth_system.auth.verify_password
def verify_password(username, password):
    """ Функция проверки аутентификации пользователя """
    result = auth_system.db.read_user_by_username(username)
    if result is None:
        return None
    if result.password == password:
        return username
