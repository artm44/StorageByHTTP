from flask_sqlalchemy  import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

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