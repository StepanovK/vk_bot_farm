from peewee import *
import config as config

db = PostgresqlDatabase(database=config.db_name, user=config.db_user, password=config.db_password,
                        host=config.db_host, port=config.db_port)

# db = SqliteDatabase(database='test.db')


class BaseModel(Model):
    class Meta:
        database = db
