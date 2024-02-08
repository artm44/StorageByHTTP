from flask_httpauth import HTTPBasicAuth


auth = HTTPBasicAuth()

# Примеры "базы данных" пользователей и их паролей
users = {
    "user1": "password1",
    "user2": "password2"
}

@auth.verify_password
def verify_password(username, password):
    """ Функция проверки аутентификации пользователя """
    if username in users and \
            users.get(username) == password:
        return username