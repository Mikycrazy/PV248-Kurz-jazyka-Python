import sys
import sqlite3
import os
import os.path
from sqlite3 import Error

import scorelib


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

def create_print(conn, print):
    sql = ''' INSERT INTO print(id, partiture, edition)
              VALUES(?,?,?) '''
    
    edition_id = create_edition(conn, print.edition)

    cur = conn.cursor()
    cur.execute(sql, (print.print_id ,'Y' if print.partiture else 'N', edition_id))
    return cur.lastrowid

def create_edition(conn, edition):
    sql = ''' INSERT INTO edition(score, name)
              VALUES(?,?) '''

    score_id = create_score(conn, edition.composition)

    cur = conn.cursor()
    cur.execute(sql, (score_id,edition.name))
    edition_id = cur.lastrowid

    for person in edition.authors:
        person_id = create_or_update_person(conn, person)
        add_author_to_edition(conn, edition_id, person_id)
        
    return edition_id

def create_score(conn, composition):
    sql = ''' INSERT INTO score(name, genre, key, incipit, year)
              VALUES(?,?,?,?,?) '''
    

    cur = conn.cursor()
    cur.execute(sql, (composition.name, composition.genre, composition.key, composition.incipit, composition.year))
    score_id = cur.lastrowid

    for idx,voice in enumerate(composition.voices):    
        create_voice(conn, score_id, idx, voice)

    for person in composition.authors:
        person_id = create_or_update_person(conn, person)
        add_author_to_score(conn, score_id, person_id)

    return score_id

def create_voice(conn, score_id, number, voice):
    sql = ''' INSERT INTO voice(number, score, range, name)
              VALUES(?,?,?,?) '''
    
    cur = conn.cursor()
    cur.execute(sql, (number, score_id, voice.range, voice.name))
    return cur.lastrowid

def add_author_to_edition(conn, edition_id, editor_id):
    sql = ''' INSERT INTO edition_author(edition, editor)
              VALUES(?,?) '''

    cur = conn.cursor()
    cur.execute("SELECT * FROM edition_author WHERE edition=? AND editor=?", (edition_id,editor_id))
    data_row = cur.fetchone()
    if data_row:
        return

    cur.execute(sql, (edition_id, editor_id))
    return

def add_author_to_score(conn, score_id, composer_id):
    sql = ''' INSERT INTO score_author(score, composer)
              VALUES(?,?) '''

    cur = conn.cursor()
    cur.execute("SELECT * FROM edition_author WHERE edition=? AND editor=?", (score_id, composer_id))
    data_row = cur.fetchone()
    if data_row:
        return

    cur.execute(sql, (score_id, composer_id))
    return

def create_or_update_person(conn, person):

    sql = ''' INSERT INTO person(born, died, name)
               VALUES(?,?,?) '''
    
    data_row = select_person_by_name(conn, person.name)
    if data_row:
        personId = int(data_row[0])
        update = False

        if person.born and not data_row[1]:
            update = True
        elif not person.born and data_row[1]:
            person.born = int(data_row[1])

        if person.died and not data_row[2]:
            update = True
        elif not person.died and data_row[2]:
            person.died = int(data_row[2])

        if update:
            update_person(conn, personId, person)

        return personId
    else:
        cur = conn.cursor()
        cur.execute(sql, (person.born, person.died, person.name))
    return cur.lastrowid

def select_person_by_name(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM person WHERE name=?", (name,))
    person = cur.fetchone()
    return person

def update_person(conn, personId, person):
    sql = ''' UPDATE person
              SET born = ? ,
                  died = ? ,
                  name = ?
              WHERE id = ?'''

    cur = conn.cursor()
    cur.execute(sql, (person.born, person.died, person.name, personId))
    return cur.lastrowid

def main():
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

    prints = scorelib.load(data_file)
    for p in prints:
        create_print(conn, p)

    conn.commit()

if __name__ == '__main__':
    main()
