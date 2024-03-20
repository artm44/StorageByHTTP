from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC

my_db = SQLAlchemy()


class Metadata(my_db.Model):
    """ Модель записи о метаданных файла """
    __tablename__ = 'metadata'

    id = my_db.Column(my_db.Integer, primary_key=True)
    username = my_db.Column(my_db.String(50), nullable=False)  # Владелец файла
    file_hash = my_db.Column(my_db.String(50), nullable=False)  # Хэш файла
    date = my_db.Column(my_db.DateTime, default=datetime.now(UTC))  # Дата добавления файла

    def __init__(self, username, file_hash):
        self.username = username
        self.file_hash = file_hash

    def __repr__(self) -> str:
        return 'Metadata %r' % self.id


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


class StorageDB:
    """ Класс для работы с базой данных """

    def __init__(self, db, app) -> None:
        self.db = db
        self.init_app(app)

    def init_app(self, app):
        self.db.init_app(app)

    def create_all(self):
        self.db.create_all()

    def drop_all(self):
        self.db.drop_all()

    def upload_metadata(self, metadata):
        self.db.session.add(metadata)
        self.db.session.commit()

    def delete_metadata(self, metadata):
        result = self.db.session.query(Metadata).filter(Metadata.file_hash == metadata.file_hash,
                                                        Metadata.username == metadata.username).first()
        self.db.session.delete(result)
        self.db.session.commit()

    def upload_user(self, user):
        self.db.session.add(user)
        self.db.session.commit()

    def delete_user(self, user):
        result = self.db.session.query(User).filter(User.username == user.username).first()
        self.db.session.delete(result)
        self.db.session.commit()

    def read_user_by_username(self, username) -> User:
        result = self.db.session.query(User).filter(User.username == username).first()
        if result:
            return result
        else:
            return None

    def get_users_by_hash(self, file_hash):
        """ Метод возвращающий всех пользователей, у которые являются владельцами файла """
        result = self.db.session.query(Metadata).filter(Metadata.file_hash == file_hash).all()
        if result:
            return [data.username for data in result]
        else:
            return None
