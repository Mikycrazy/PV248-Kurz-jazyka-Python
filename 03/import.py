import sys
import sqlite3
import os
import os.path
from sqlite3 import Error

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None


def create_db(conn, create_db_file):
    try:
        c = conn.cursor()
        with open(create_db_file, 'r') as f:
            c.executescript(f.read())
    except Error as e:
        print(e)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        exit("Too less arguments calling script")

    data_file = sys.argv[1]
    db_file = sys.argv[2]
    create_db_file = "scorelib.sql"

    # Delete the old table
    if os.path.isfile(db_file):
        os.remove(db_file)

    # create a database connection
    conn = create_connection(db_file)

    if conn is not None:
        create_db(conn, create_db_file)
    else:
        print("Error! cannot create the database connection.")