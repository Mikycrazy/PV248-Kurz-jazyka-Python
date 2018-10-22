import sys
import sqlite3
import os
import os.path
from sqlite3 import Error

import scorelib
from scorelib import Voice


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
    
    edition_id = create_or_get_edition(conn, print.edition)

    cur = conn.cursor()
    cur.execute(sql, (print.print_id ,'Y' if print.partiture else 'N', edition_id))
    return cur.lastrowid

def create_or_get_edition(conn, edition):

    edition_id = try_get_edition(conn, edition)
    if edition_id:
        return edition_id

    sql = ''' INSERT INTO edition(score, name)
            VALUES(?,?) '''

    score_id = create_or_get_score(conn, edition.composition)

    cur = conn.cursor()
    cur.execute(sql, (score_id,edition.name))
    edition_id = cur.lastrowid

    for person in edition.authors:
        person_id = create_or_update_person(conn, person)
        add_author_to_edition(conn, edition_id, person_id)
        
    return edition_id

def try_get_edition(conn, edition):
    select_sql = ''' SELECT * FROM edition WHERE name=?'''

    cur = conn.cursor()
    cur.execute(select_sql, (edition.name,))
    rows = cur.fetchall()

    score_id = get_score_id(conn, edition.composition)
    if not score_id:
        return None

    for row in rows:
        edition_id = row[0]

        editors_match = True
        actual_editor_ids = get_editor_ids_by_edition(conn, edition_id)
        current_editor_ids = []
        for person in edition.authors:
            data_row = select_person_row_by_name(conn, person.name)
            if data_row:
                current_editor_ids.append(int(data_row[0]))
            else:
                editors_match = False
                break

        if editors_match:
            editors_match = set(actual_editor_ids) == set(current_editor_ids)

        if score_id == row[1] and editors_match:
            return edition_id
    return None

def get_score_id(conn, composition):
    select_sql = ''' SELECT * FROM score WHERE name=? and genre=? and key=? and incipit=?'''

    cur = conn.cursor()
    cur.execute(select_sql, (composition.name, composition.genre, composition.key, composition.incipit))
    rows = cur.fetchall()
    for row in rows:
        score_id = row[0]
        voices_match, composers_match = (True, True)
        voices = get_voices_by_score(conn, score_id)
        if(len(voices) == len(composition.voices)):
            for idx,voice in enumerate(composition.voices):
                expected_voice = voices[idx]
                if voice.name != expected_voice.name or voice.range != expected_voice.range:
                    voices_match = False
                    break
        else:
            voices_match = False

        actual_author_ids = get_author_ids_by_score(conn, score_id)
        current_author_ids = []
        for person in composition.authors:
            data_row = select_person_row_by_name(conn, person.name)
            if data_row:
                current_author_ids.append(int(data_row[0]))
            else:
                composers_match = False
                break
        
        if composers_match:
            composers_match = set(actual_author_ids) == set(current_author_ids)

        if voices_match and composers_match:
            return score_id

    return None

def create_or_get_score(conn, composition):

    score_id = get_score_id(conn, composition)

    if score_id is not None:
        return score_id

    insert_score_sql = ''' INSERT INTO score(name, genre, key, incipit, year)
              VALUES(?,?,?,?,?) '''

    cur = conn.cursor()
    cur.execute(insert_score_sql, (composition.name, composition.genre, composition.key, composition.incipit, composition.year))
    score_id = cur.lastrowid

    for idx,voice in enumerate(composition.voices):    
        create_voice(conn, score_id, idx + 1, voice)

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

def get_voices_by_score(conn, score_id):
    sql = ''' SELECT id, name, range FROM voice WHERE score = ?'''
    cur = conn.cursor()
    cur.execute(sql, (score_id,))
    rows = cur.fetchall()

    voices = []
    for row in rows:
        voices.append(Voice(row[1], row[2]))

    return voices

def get_author_ids_by_score(conn, score_id):
    sql = ''' SELECT composer FROM score_author WHERE score = ?'''
    cur = conn.cursor()
    cur.execute(sql, (score_id,))
    rows = cur.fetchall()
    return [int(row[0]) for row in rows]

def get_editor_ids_by_edition(conn, edition_id):
    sql = ''' SELECT editor FROM edition_author WHERE edition = ?'''
    cur = conn.cursor()
    cur.execute(sql, (edition_id,))
    rows = cur.fetchall()
    return [int(row[0]) for row in rows]


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
    
    data_row = select_person_row_by_name(conn, person.name)
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

def select_person_row_by_name(conn, name):
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
