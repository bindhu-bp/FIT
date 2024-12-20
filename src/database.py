import pymysql
import pymysql.cursors
from contextlib import contextmanager
from .config import DB_CONFIG

@contextmanager
def get_db_connection():
    connection = pymysql.connect(
        **DB_CONFIG,
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        yield connection
    finally:
        connection.close()