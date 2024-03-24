from flask import Flask
from .database import my_db as db


def create_app():
    app = Flask(__name__)
    # app.config.from_object(os.environ['APP_SETTINGS'])
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metadata.db'

    import app.usermodule.controllers as firstmodule

    app.register_blueprint(firstmodule.module)

    import app.filemodule.controllers as secondmodule

    app.register_blueprint(secondmodule.module)

    import app.swaggermodule.controllers as thirdmodule

    app.register_blueprint(thirdmodule.module)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app
