from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

my_db = SQLAlchemy()


# Декоратор для подтверждения выполнения операций CUD в БД
def commit_db_operation(func):
    def wrapper(*args, **kwargs) -> bool:
        try:
            func(*args, **kwargs)
        except exc.SQLAlchemyError as ex:
            print(ex)
            return False
        return True

    return wrapper
