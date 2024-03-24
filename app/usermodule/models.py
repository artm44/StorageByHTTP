from datetime import datetime, UTC

from app.database import my_db, commit_db_operation


class User(my_db.Model):
    """ Модель записи о зарегистрированных пользователей """
    __tablename__ = 'user'

    id = my_db.Column(my_db.Integer, primary_key=True)
    username = my_db.Column(my_db.String(50), nullable=False, unique=True)
    password = my_db.Column(my_db.String(50), nullable=False)
    date = my_db.Column(my_db.DateTime, default=datetime.now(UTC))  # Дата регистрации пользователя

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self) -> str:
        return 'Metadata %r' % self.id


class UserDB:
    """ Класс для работы с таблицей User """

    def __init__(self, db) -> None:
        self.db = db

    @commit_db_operation
    def upload_user(self, user: User):
        self.db.session.add(user)
        self.db.session.commit()

    @commit_db_operation
    def delete_user(self, user: User):
        result = self.db.session.query(User).filter(User.username == user.username).first()
        self.db.session.delete(result)
        self.db.session.commit()

    def read_user_by_username(self, username: str) -> User:
        result = self.db.session.query(User).filter(User.username == username).first()
        return result
