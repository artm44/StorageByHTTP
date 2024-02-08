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
    
class MetadataDB:
    def __init__(self, app=None) -> None:
         if app is not None:
             db.init_app(app)

    def create_all(self):
        db.create_all()
    
    def upload_metadata(self, metadata):
        print(db.session.add(metadata))
        db.session.commit()
    
    def delete_metadata(self, metadata):
        result = db.session.query(Metadata).filter(Metadata.file_hash == metadata.file_hash, \
                                                        Metadata.username == metadata.username).first()
        db.session.delete(result)
        db.session.commit()
        
    def get_users_by_hash(self, file_hash):
        result = db.session.query(Metadata).filter(Metadata.file_hash == file_hash).all()
        if result:
            return [data.username for data in result]
        else:
            return None