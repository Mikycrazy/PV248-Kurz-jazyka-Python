import sqlite3
from sqlite3 import Error
from .model import Person, Print, Voice


def get_composers(print_id):

    conn = create_connection('scorelib.dat')

    sql = '''   SELECT PE.name, PE.born, PE.died
                FROM [print] P
                JOIN edition E ON E.id = P.edition
                JOIN score S ON S.id = E.score
                JOIN score_author sa ON sa.score = s.id
                JOIN person PE ON PE.id = sa.composer
                WHERE P.id = ? '''
    
    cur = conn.cursor()
    rows = cur.execute(sql, (print_id,))
    
    composers = []
    for row in rows:
        composers.append(Person(row[0], row[1], row[2]))

    return composers

def get_print(name):
    conn = create_connection('scorelib.dat')

    composers = get_composers_by_name(conn, name)
    composers_prints = {}
    for id,composer in composers.items():
        composers_prints[composer.name] = get_prints(conn, id)
    return composers_prints

def get_composers_by_name(conn, name):
    sql = '''   SELECT P.id, P.name, P.born, P.died
                FROM Person P
                WHERE P.name LIKE ?'''

    cur = conn.cursor()
    rows = cur.execute(sql, ('%'+name+'%',))
    return { row[0]:Person(row[1], row[2], row[3]) for row in rows }

def get_prints(conn, composer_id):
    sql = '''   SELECT 
                    P.id, P.partiture,
                    E.id as edition_id, E.name, E.year,
                    S.id as score_id, S.name as title, S.genre, S.key, S.incipit, S.year
                FROM print P
                JOIN edition E ON E.id = P.edition
                JOIN score S ON S.id = E.score
                JOIN score_author SA ON SA.score = S.id
                JOIN person PE ON PE.id = SA.composer
                WHERE PE.id = ? '''

    cur = conn.cursor()
    rows = cur.execute(sql, (composer_id,))
    prints = []
    for row in rows:
        print_id = int(row[0])
        partiture = (True if row[1] == 'Y' else False)
        edition_id = int(row[2])
        edition_name = row[3]
        edition_year = row[4]
        score_id = row[5]
        title = row[6]
        genre = row[7]
        key = row[8]
        incipit = row[9]
        composition_year = row[10]

        editors = get_editors(conn, edition_id)
        voices = get_voices(conn, score_id)
        composers = get_composers(print_id)

        print_obj = Print(print_id, partiture, edition_name, editors, title, incipit, key, genre, composition_year, voices, composers)
        prints.append(print_obj)
    return prints


def get_editors(conn, edition_id):
    sql = '''   SELECT person.*
                FROM person
                JOIN edition_author ON edition_author.editor = person.id
                WHERE edition_author.edition = ? '''

    cur = conn.cursor()
    rows = cur.execute(sql, (edition_id,))
    return [Person(row[0], row[1], row[2]) for row in rows]

def get_voices(conn, score_id):
    sql = '''   SELECT voice.name, voice.range, voice.number
                FROM voice
                WHERE voice.score = ? '''

    cur = conn.cursor()
    rows = cur.execute(sql, (score_id,))
    return [Voice(row[0], row[1]) for row in rows]


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

