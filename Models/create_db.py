import config as config
import psycopg2
import psycopg2.extras
from config import logger
from Models.base import db
from Models.Telegram import TelegramUser
from Models.Accounts import Account
from Models.Tasks import Task, BotTask, Script


def recreate_database():
    if config.debug:
        logger.info('Database update:')

    if config.debug:
        logger.info('1 - Dropping the database. Start')
    deleted = delete_database()
    if not deleted:
        return False
    if config.debug:
        logger.info('1 - Dropping the database. Completed')

    if config.debug:
        logger.info('2 - Creating the database. Start')
    db_created = create_database()
    if not db_created:
        return False
    if config.debug:
        logger.info('2 - Creating the database. Completed')

    if config.debug:
        logger.info('3 - Creating tables. Start')
    tbls_created = create_all_tables()
    if not tbls_created:
        return False
    if config.debug:
        logger.info('3 - Creating tables. Completed')

    if config.debug:
        logger.info('Database update completed!')
    return True


def create_all_tables():
    result = False
    models = [
        TelegramUser,
        Account,
        Task,
        BotTask,
        Script,
    ]
    with db:
        db.create_tables(models)
        result = True
    return result


def get_pg_connection():
    try:
        connection = psycopg2.connect(
            host=config.db_host,
            port=config.db_port,
            user=config.db_user,
            password=config.db_password
        )
        return connection
    except Exception as ex:
        connection_info = f'host={config.db_host}, port={config.db_port},' \
                          f' user={config.db_user} password={config.db_password}'
        logger.error(f"Problem connecting to PostgreSQL\n({connection_info}):", ex)
        return None


def delete_database():
    result = False
    conn = get_pg_connection()
    conn.autocommit = True
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                f"""DROP DATABASE IF EXISTS {config.db_name};"""
            )
            result = True
        except Exception as ex:
            logger.error(f'Failed to drop database.\n{ex}')
    conn.close()
    return result


def create_database():
    result = False
    conn = get_pg_connection()
    conn.autocommit = True
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                f"""CREATE DATABASE {config.db_name}
                    WITH 
                    OWNER = postgres
                    ENCODING = 'UTF8'
                    TABLESPACE = pg_default
                    CONNECTION LIMIT = -1;"""
            )
            result = True
        except Exception as ex:
            logger.error(f'Failed to create database.\n{ex}')
    conn.close()
    return result


if __name__ == '__main__':
    recreate_database()
