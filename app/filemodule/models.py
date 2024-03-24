from datetime import datetime, UTC

from app.database import my_db, commit_db_operation


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


class MetadataDB:
    """ Класс для работы с таблицей Metadata """

    def __init__(self, db) -> None:
        self.db = db

    @commit_db_operation
    def upload_metadata(self, metadata: Metadata):
        self.db.session.add(metadata)
        self.db.session.commit()

    @commit_db_operation
    def delete_metadata(self, metadata: Metadata):
        result = self.db.session.query(Metadata).filter(Metadata.file_hash == metadata.file_hash,
                                                        Metadata.username == metadata.username).first()
        self.db.session.delete(result)
        self.db.session.commit()

    def get_users_by_hash(self, file_hash: str) -> [str]:
        """ Метод возвращающий всех пользователей, у которые являются владельцами файла """
        result = self.db.session.query(Metadata).filter(Metadata.file_hash == file_hash).all()
        if result is None:
            return []
        return [data.username for data in result]
