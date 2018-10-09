import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        conn.close()

def create_db(conn, create_db_script_file):
    try:
        c = conn.cursor()
        with open(create_db_script_file, 'r') as f:
            c.execute(f.read())
    except Error as e:
        print(e)